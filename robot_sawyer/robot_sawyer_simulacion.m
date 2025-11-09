% ==============================================================
% Programa desarrollado por Marcela Padilla
% Control del robot Sawyer mediante gestos y comunicación UDP
% ==============================================================
% Este script permite controlar las siete articulaciones del robot Sawyer 
% a través de gestos detectados por el sensor Leap Motion y enviados desde 
% Python mediante comunicación UDP. 
%
% Cada gesto se asocia a una articulación específica, y el sistema actualiza 
% las posiciones articulares dentro de límites definidos, mostrando en tiempo 
% real el movimiento del robot y el valor de cada junta mediante sliders. 
% El programa también permite mover manualmente las juntas con los sliders 
% y actualiza el modelo 3D del robot en la misma figura.
% ==============================================================

clc; clear;

% --------------------------------------------------------------
% CONFIGURACIÓN DEL ROBOT SAWYER
% --------------------------------------------------------------
sawyer = cargar_sawyer();       % Cargar modelo DH aproximado del Sawyer
q = zeros(1,7);                 % Posición inicial de las 7 articulaciones

% --------------------------------------------------------------
% LÍMITES DE MOVIMIENTO Y PARÁMETROS DE REBOTE
% --------------------------------------------------------------
delta  = 0.2;                   % Paso de movimiento base
qmin   = -pi*ones(1,7);         % Límite inferior por articulación
qmax   =  pi*ones(1,7);         % Límite superior
dstep  =  delta*ones(1,7);      % Paso independiente por junta (invierte signo al rebotar)

% --------------------------------------------------------------
% CONFIGURACIÓN DE INTERFAZ VISUAL (robot + sliders)
% --------------------------------------------------------------
f = figure('Name','Control por Gestos - Sawyer','Position',[100 100 1200 600], ...
           'Color','w','NumberTitle','off');

% Panel del robot (lado izquierdo)
ax = axes('Parent', f, 'Units','normalized', 'Position', [0.05 0.08 0.62 0.88]);
view(ax, 45, 20); grid(ax, 'on'); box(ax, 'on');

% Dibuja el robot en los ejes
axes(ax); %#ok<LAXES>
sawyer.plot(q, 'workspace', [-1000 1000 -1000 1000 -100 1200], 'delay', 0);

% Panel de control (lado derecho)
pnl = uipanel('Parent', f, 'Title','Juntas', 'FontWeight','bold', ...
              'Units','normalized', 'Position',[0.70 0.08 0.27 0.88]);

% Creación de sliders y etiquetas
sliders = gobjects(1,7);
labels  = ["J1","J2","J3","J4","J5","J6","J7"];
for i = 1:7
    uicontrol(pnl, 'Style','text', 'String', labels(i), ...
        'Units','normalized', 'Position',[0.05, 1 - i*0.13 + 0.07, 0.15, 0.08], ...
        'HorizontalAlignment','left', 'FontWeight','bold', 'BackgroundColor','w');
    sliders(i) = uicontrol(pnl, 'Style','slider', ...
        'Min', qmin(i), 'Max', qmax(i), 'Value', q(i), ...
        'Units','normalized', 'Position',[0.22, 1 - i*0.13 + 0.08, 0.73, 0.06], ...
        'Callback', @(s,~) onSliderMove());
end

% --------------------------------------------------------------
% CONFIGURACIÓN DE GESTOS Y TEMPORIZACIÓN
% --------------------------------------------------------------
lastGesto    = "";
minTiempo    = 0.05;  % Tiempo mínimo entre gestos válidos
ultimoTiempo = tic;

% --------------------------------------------------------------
% CONFIGURACIÓN DE COMUNICACIÓN UDP
% --------------------------------------------------------------
u = udpport("datagram","IPV4","LocalPort",50011);
disp("Esperando gestos desde Python...");

% Limpieza al cerrar
set(f, 'CloseRequestFcn', @(src,evt) onClose(src,evt,u));

% Publicar variables en base (para accesibilidad en callbacks)
assignin('base','sawyer', sawyer);
assignin('base','q', q);
assignin('base','qmin', qmin);
assignin('base','qmax', qmax);

% --------------------------------------------------------------
% BUCLE PRINCIPAL DE CONTROL
% --------------------------------------------------------------
while ishandle(f)
    % Leer comandos si hay datos UDP disponibles
    if u.NumDatagramsAvailable > 0
        d = read(u, 1, "string");
        gesto = strtrim(d.Data);

        % Procesa gesto si es nuevo o ha pasado tiempo mínimo
        if ~strcmpi(gesto, lastGesto) || toc(ultimoTiempo) > minTiempo
            disp("Gesto recibido: " + gesto);
            lastGesto = gesto;
            ultimoTiempo = tic;

            % Mapeo de gestos a articulaciones
            switch lower(gesto)
                case "cerrada",               [q,dstep] = stepBounce(q, dstep, 1, qmin, qmax, delta);
                case "cerrada derecha",       [q,dstep] = stepBounce(q, dstep, 2, qmin, qmax, delta);
                case "cerrada izquierda",     [q,dstep] = stepBounce(q, dstep, 3, qmin, qmax, delta);
                case "abierta",               [q,dstep] = stepBounce(q, dstep, 4, qmin, qmax, delta);
                case "abierta derecha",       [q,dstep] = stepBounce(q, dstep, 5, qmin, qmax, delta);
                case "abierta izquierda",     [q,dstep] = stepBounce(q, dstep, 6, qmin, qmax, delta);
                case "derecha completa",      [q,dstep] = stepBounce(q, dstep, 7, qmin, qmax, delta);
            end

            % Actualiza sliders y visualización del robot
            for i = 1:7
                sliders(i).Value = q(i);
            end
            sawyer.animate(q);
            assignin('base','q', q);
            drawnow;
        end
    end
    pause(0.01); % Espera pequeña para lectura natural
end

% --------------------------------------------------------------
% FUNCIONES AUXILIARES
% --------------------------------------------------------------

function onSliderMove()
    % Permite mover las articulaciones manualmente con los sliders
    f = gcf; % Figura actual
    pnl = findobj(f, 'Type','uipanel', '-and', 'Title','Juntas');
    slds = findobj(pnl, 'Style','slider');
    % Ordenar sliders verticalmente (de J1 a J7)
    [~, idx] = sort(arrayfun(@(h) h.Position(2), slds), 'descend');
    slds = slds(idx);
    qloc = zeros(1,7);
    qmin = evalin('base','qmin');
    qmax = evalin('base','qmax');
    for k = 1:7
        qloc(k) = min(slds(k).Max, max(slds(k).Min, slds(k).Value));
        slds(k).Value = qloc(k);
    end
    sawyer = evalin('base','sawyer');
    sawyer.animate(qloc);
    assignin('base','q', qloc);
    drawnow;
end

function onClose(src, ~, u)
    % Cierre seguro del puerto UDP y ventana
    try, clear u; catch, end
    delete(src);
end

function [q, dstep] = stepBounce(q, dstep, i, qmin, qmax, base_step)
    % Incrementa la articulación i y rebota en límites invirtiendo la dirección
    q(i) = q(i) + dstep(i);
    if q(i) >= qmax(i)
        q(i)     = qmax(i);
        dstep(i) = -abs(base_step); % Rebote negativo
    elseif q(i) <= qmin(i)
        q(i)     = qmin(i);
        dstep(i) =  abs(base_step); % Rebote positivo
    end
end

function robot = cargar_sawyer()
    % Definición del modelo DH aproximado del robot Sawyer (en mm)
    J1 = Revolute('d', 317,   'a', 81,   'alpha', -pi/2, 'offset', 0);
    J2 = Revolute('d', 192.5, 'a', 0,    'alpha', -pi/2, 'offset', -pi/2);
    J3 = Revolute('d', 400,   'a', 0,    'alpha', -pi/2, 'offset', 0);
    J4 = Revolute('d', 168.5, 'a', 0,    'alpha', -pi/2, 'offset', pi);
    J5 = Revolute('d', 400,   'a', 0,    'alpha', -pi/2, 'offset', 0);
    J6 = Revolute('d', 136.3, 'a', 0,    'alpha', -pi/2, 'offset', pi);
    J7 = Revolute('d', 133.75,'a', 0,    'alpha', 0,     'offset', -pi/2);
    robot = SerialLink([J1 J2 J3 J4 J5 J6 J7], 'name', 'SAWYER');
end


