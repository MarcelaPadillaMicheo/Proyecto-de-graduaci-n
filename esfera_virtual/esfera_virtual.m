clc
clear

u = udpport("datagram", "IPV4", "LocalPort", 50010);
disp("Esperando gestos desde Python...");

x = 0; y = 0; delta = 0.05;
activo = true;

fig = figure('Name', 'Joystick Gestual', 'NumberTitle', 'off');
axis([-30 30 -30 30]); hold on;
punto = plot(x, y, 'bo', 'MarkerSize', 12, 'MarkerFaceColor', 'b');
textLabel = text(0, -28, '', 'HorizontalAlignment', 'center', 'FontSize', 14);

while ishandle(fig)
    if u.NumDatagramsAvailable > 0
        d = read(u, 1, "string");
        gesto = strtrim(d.Data);
        disp(" Gesto recibido: " + gesto);

        if strcmpi(gesto, "parar")
            activo = false;
            textLabel.String = ' Movimiento detenido';
        else
            activo = true;
        end

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

        punto.XData = x;
        punto.YData = y;
    end

    drawnow limitrate;
end
