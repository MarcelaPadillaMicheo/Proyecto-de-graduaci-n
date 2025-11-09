% ==============================================================
% Programa desarrollado por Marcela Padilla
% Control de un Agente Virtual que se mueve en el eje X, Y y alrededor del eje Z
% ==============================================================
% Este script recibe gestos desde Python por comunicación UDP
% y actualiza en tiempo real la posición de un punto que representa al agente.
% Los gestos determinan la dirección del movimiento en el plano (X,Y).
% ==============================================================

clc
clear

% --------------------------------------------------------------
% Configuración del puerto UDP para recibir datos desde Python
% --------------------------------------------------------------
u = udpport("datagram", "IPV4", "LocalPort", 50010);
disp("Esperando gestos desde Python...");

% --------------------------------------------------------------
% Variables iniciales
% --------------------------------------------------------------
x = 0;             % Posición inicial en eje X
y = 0;             % Posición inicial en eje Y
delta = 0.05;      % Incremento de movimiento por gesto
activo = true;     % Estado del agente (activo/inactivo)

% --------------------------------------------------------------
% Configuración de la figura y elementos gráficos
% --------------------------------------------------------------
fig = figure('Name', 'Joystick Gestual', 'NumberTitle', 'off');
axis([-30 30 -30 30]); hold on;
punto = plot(x, y, 'bo', 'MarkerSize', 12, 'MarkerFaceColor', 'b');
textLabel = text(0, -28, '', 'HorizontalAlignment', 'center', 'FontSize', 14);

% --------------------------------------------------------------
% Bucle principal: se ejecuta mientras la ventana esté abierta
% --------------------------------------------------------------
while ishandle(fig)
    
    % Verifica si hay datagramas disponibles desde Python
    if u.NumDatagramsAvailable > 0
        
        % Lectura del gesto recibido (tipo string)
        d = read(u, 1, "string");
        gesto = strtrim(d.Data);  % Elimina espacios en blanco
        disp(" Gesto recibido: " + gesto);
        
        % ----------------------------------------------------------
        % Control de activación: si el gesto es "parar", detiene el movimiento
        % ----------------------------------------------------------
        if strcmpi(gesto, "parar")
            activo = false;
            textLabel.String = ' Movimiento detenido';
        else
            activo = true;
        end

        % ----------------------------------------------------------
        % Actualización de la posición según el gesto detectado
        % ----------------------------------------------------------
        if activo
            switch lower(gesto)
                case "abierta"
                    y = y + delta;
                    textLabel.String = 'Avanzar recto';
                case "cerrada"
                    y = y - delta;
                    textLabel.String = 'Retroceder';
                case "abierta derecha"
                    x = x + delta; y = y + delta;
                    textLabel.String = 'Diagonal arriba derecha';
                case "abierta izquierda"
                    x = x - delta; y = y + delta;
                    textLabel.String = 'Diagonal arriba izquierda';
                case "cerrada derecha"
                    x = x + delta; y = y - delta;
                    textLabel.String = 'Diagonal abajo derecha';
                case "cerrada izquierda"
                    x = x - delta; y = y - delta;
                    textLabel.String = 'Diagonal abajo izquierda';
                otherwise
                    textLabel.String = 'Gesto desconocido';
            end
        end

        % ----------------------------------------------------------
        % Actualiza la posición del punto en la figura
        % ----------------------------------------------------------
        punto.XData = x;
        punto.YData = y;
    end

    % ----------------------------------------------------------
    % Actualiza la visualización en tiempo real
    % ----------------------------------------------------------
    drawnow limitrate;
end


