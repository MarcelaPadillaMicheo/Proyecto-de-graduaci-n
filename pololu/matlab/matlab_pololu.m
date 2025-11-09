% ==============================================================
% Programa desarrollado por Marcela Padilla
% Control del robot físico Pololu 3Pi+ en MATLAB mediante UDP
% ==============================================================
% Este script recibe gestos en tiempo real enviados por Python a través
% de comunicación UDP y los traduce a comandos de movimiento para el 
% robot Pololu 3Pi+ físico. 
% Cada gesto controla las velocidades lineal y angular del robot, 
% permitiendo avanzar, retroceder, girar y detenerse. 
% Además, se muestra la trayectoria recorrida del robot en tiempo real.
% ==============================================================

function pololu3pi_real_udp_visual
    % ----------------------------------------------------------
    % PARÁMETROS DE CONFIGURACIÓN
    % ----------------------------------------------------------
    offset = 33.6573;            % Offset de orientación del robot (ajustar según calibración)
    wheel_radius = 16;           % Radio de rueda [mm]
    wheel_distance = 96 - 2*6.8; % Distancia entre ruedas [mm]
    v_max = 400;                 % Velocidad máxima [rpm]

    % Funciones anónimas para conversión y saturación
    rads2rpm = @(x) x * (60 / (2*pi));
    velsat = @(vel) sign(vel) * min(abs(vel), v_max);

    % ----------------------------------------------------------
    % PARÁMETROS DEL CONTROLADOR
    % ----------------------------------------------------------
    v = 0; w = 0;                % Inicialización de velocidades
    v_cmd = 0.15;                % Velocidad lineal de referencia [m/s]
    w_cmd = 0.4;                 % Velocidad angular de referencia [rad/s]

    % ----------------------------------------------------------
    % CONFIGURACIÓN DE COMUNICACIÓN UDP
    % ----------------------------------------------------------
    u = udpport("datagram", "IPV4", "LocalPort", 5006, "Timeout", 0.01);
    disp("Pololu físico escuchando comandos por UDP...");

    % ----------------------------------------------------------
    % VARIABLES PARA VISUALIZACIÓN DE TRAYECTORIA
    % ----------------------------------------------------------
    traj_x = [];
    traj_y = [];

    % ----------------------------------------------------------
    % CONFIGURACIÓN DE FIGURA PARA MONITOREO
    % ----------------------------------------------------------
    figure('Name', 'Trayectoria Pololu 3Pi');
    h = plot(0, 0, 'bo', 'MarkerSize', 10, 'MarkerFaceColor', 'b');
    hold on;
    axis equal;
    grid on;
    xlabel('X [mm]');
    ylabel('Y [mm]');
    traj = animatedline('Color', 'k', 'LineStyle', '--');

    % ----------------------------------------------------------
    % BUCLE PRINCIPAL DE EJECUCIÓN
    % ----------------------------------------------------------
    while true
        % Leer gestos enviados por Python
        if u.NumDatagramsAvailable > 0
            d = read(u, 1, "string");
            gesto = strtrim(d.Data);
            disp("Gesto recibido: " + gesto);

            % Mapeo de gestos a comandos de velocidad
            switch lower(gesto)
                case "abierta"
                    v = v_cmd; w = 0;                   % Avanzar
                case "cerrada"
                    v = -v_cmd; w = 0;                  % Retroceder
                case "abierta derecha"
                    v = v_cmd; w = -w_cmd;              % Girar derecha
                case "abierta izquierda"
                    v = v_cmd; w = w_cmd;               % Girar izquierda
                case "cerrada derecha"
                    v = -v_cmd; w = -w_cmd;             % Retroceder girando derecha
                case "cerrada izquierda"
                    v = -v_cmd; w = w_cmd;              % Retroceder girando izquierda
                case "parar"
                    v = 0; w = 0;                       % Detenerse
            end
        end

        % ------------------------------------------------------
        % CONVERSIÓN A VELOCIDADES DE CADA RUEDA
        % ------------------------------------------------------
        vL = (2*v - w*(wheel_distance/1000)) / (2*(wheel_radius/1000));
        vR = (2*v + w*(wheel_distance/1000)) / (2*(wheel_radius/1000));

        v_left_rpm = velsat(rads2rpm(vL));
        v_right_rpm = velsat(rads2rpm(vR));

        % ------------------------------------------------------

