function pololu3pi_real_udp_visual
    offset = 33.6573; % Usa el offset correspondiente a tu robot

    % Parámetros físicos
    wheel_radius = 16; % mm
    wheel_distance = 96 - 2*6.8; % mm
    v_max = 400; % rpm

    rads2rpm = @(x) x * (60 / (2*pi));
    velsat = @(vel) sign(vel) * min(abs(vel), v_max);

    % Parámetros del controlador
    v = 0; w = 0;
    v_cmd = 0.15; % prueba con más velocidad si no se mueve
    w_cmd = 0.4;

    % UDP
    u = udpport("datagram", "IPV4", "LocalPort", 5006, "Timeout", 0.01);
    disp("Pololu físico escuchando comandos por UDP...");

    % Variables para visualización
    traj_x = [];
    traj_y = [];

    % Visual
    figure('Name', 'Trayectoria Pololu 3Pi');
    h = plot(0, 0, 'bo', 'MarkerSize', 10, 'MarkerFaceColor', 'b');
    hold on;
    axis equal;
    grid on;
    xlabel('X [mm]');
    ylabel('Y [mm]');
    traj = animatedline('Color', 'k', 'LineStyle', '--');

    while true
        % Leer comandos UDP
        if u.NumDatagramsAvailable > 0
            d = read(u, 1, "string");
            gesto = strtrim(d.Data);
            disp("Gesto recibido: " + gesto);

            switch lower(gesto)
                case "abierta"
                    v = v_cmd; w = 0;
                case "cerrada"
                    v = -v_cmd; w = 0;
                case "abierta derecha"
                    v = v_cmd; w = -w_cmd;
                case "abierta izquierda"
                    v = v_cmd; w = w_cmd;
                case "cerrada derecha"
                    v = -v_cmd; w = -w_cmd;
                case "cerrada izquierda"
                    v = -v_cmd; w = w_cmd;
                case "parar"
                    v = 0; w = 0;
            end
        end

        % Conversion a velocidades de rueda
        vL = (2*v - w*(wheel_distance/1000)) / (2*(wheel_radius/1000));
        vR = (2*v + w*(wheel_distance/1000)) / (2*(wheel_radius/1000));

        v_left_rpm = velsat(rads2rpm(vL));
        v_right_rpm = velsat(rads2rpm(vR));

        % Enviar a robot
        robotat_3pi_set_wheel_velocities(robot, -v_right_rpm, -v_left_rpm);

        % Leer pose del robot
        pose = robotat_get_pose(robotat, robot_no, 'eulzyx');
        x_mm = pose(1)*1000;
        y_mm = pose(2)*1000;
        theta_deg = atan2d(sind(pose(4)-offset), cosd(pose(4)-offset));

        % Actualizar visual
        set(h, 'XData', x_mm, 'YData', y_mm);
        addpoints(traj, x_mm, y_mm);
        drawnow;

        pause(0.05);
    end
end
