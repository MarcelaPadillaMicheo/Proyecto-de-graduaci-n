function pololu3pi_controller
addpath('robotat'); % para funciones de Robotat

TIME_STEP = 64;

% Parámetros del robot
wheel_radius = 32; % mm
wheel_distance = 96 - 2*6.8; % mm

% Dispositivos
right_motor = wb_robot_get_device('motor_1');
left_motor = wb_robot_get_device('motor_2');
compass = wb_robot_get_device('compass');
gps = wb_robot_get_device('gps');

wb_gps_enable(gps, 10);
wb_compass_enable(compass, 10);

% Velocidad máxima en rpm
v_max = 800 / 2;

% Conversión rpm <-> rad/s
rads2rpm = @(x) x * (60 / (2*pi));
rpm2rads = @(x) x * (2*pi / 60);
velsat = @(vel) sign(vel) * min(abs(vel), v_max);

% Inicializar motores
wb_motor_set_position(left_motor, inf);
wb_motor_set_position(right_motor, inf);
wb_motor_set_velocity(left_motor, 0.0);
wb_motor_set_velocity(right_motor, 0.0);

% Configurar archivo temporal para Windows
TEMP_FILE_PATH = fullfile(getenv('TEMP'), 'leap_motion_command.txt');

% Inicializar velocidad
v = 0; w = 0;
v_cmd = 0.1; % velocidad lineal base
w_cmd = 0.3; % velocidad angular base

disp("Pololu escuchando comandos desde archivo temporal...");
disp(["Archivo: " TEMP_FILE_PATH]);

% Variable para evitar procesar el mismo comando múltiples veces
ultimo_gesto = "";
ultimo_tiempo = 0;

while wb_robot_step(TIME_STEP) ~= -1
    % Leer comando del archivo si existe
    if exist(TEMP_FILE_PATH, 'file')
        try
            % Leer el archivo
            fid = fopen(TEMP_FILE_PATH, 'r');
            if fid ~= -1
                gesto = strtrim(fgets(fid));
                fclose(fid);
                
                % Solo procesar si es un gesto nuevo
                if ~isempty(gesto) && ~strcmp(gesto, ultimo_gesto)
                    disp("Gesto recibido: " + gesto);
                    ultimo_gesto = gesto;
                    ultimo_tiempo = wb_robot_get_time();
                    
                    % Traducir gesto a velocidades v y w
                    switch lower(gesto)
                        case "abierta"
                            v = v_cmd; w = 0;
                        case "cerrada"
                            v = -v_cmd; w = 0;
                        case "abierta_derecha"
                            v = v_cmd; w = -w_cmd;
                        case "abierta_izquierda"
                            v = v_cmd; w = w_cmd;
                        case "cerrada_derecha"
                            v = -v_cmd; w = -w_cmd;
                        case "cerrada_izquierda"
                            v = -v_cmd; w = w_cmd;
                        case "parar"
                            v = 0; w = 0;
                        otherwise
                            % mantener el último comando si no se reconoce
                    end
                end
            end
        catch
            % Ignorar errores de lectura
        end
    end
    
    % Limpiar archivo después de 2 segundos sin cambios
    tiempo_actual = wb_robot_get_time();
    if ~isempty(ultimo_gesto) && (tiempo_actual - ultimo_tiempo) > 2.0
        try
            if exist(TEMP_FILE_PATH, 'file')
                delete(TEMP_FILE_PATH);
                ultimo_gesto = "";
            end
        catch
        end
    end

    % Convertir velocidades (modelo uniciclo → diferencial)
    vL = (2*v - w*wheel_distance/1000) / (2 * wheel_radius/1000); % rad/s
    vR = (2*v + w*wheel_distance/1000) / (2 * wheel_radius/1000);

    % Convertir a rpm y saturar
    v_left = velsat(rads2rpm(vL));
    v_right = velsat(rads2rpm(vR));

    % Enviar a motores
    wb_motor_set_velocity(left_motor, -rpm2rads(v_left));
    wb_motor_set_velocity(right_motor, -rpm2rads(v_right));

    drawnow;
end

% Limpiar al finalizar
try
    if exist(TEMP_FILE_PATH, 'file')
        delete(TEMP_FILE_PATH);
    end
catch
end