clc; clear;

% === ROBOT ===
sawyer = cargar_sawyer();
q = zeros(1,7);

% === LÍMITES Y REBOTE ===
delta  = 0.2;                      % paso base
qmin   = -pi*ones(1,7);            % límites inferiores (ajusta si tienes límites reales)
qmax   =  pi*ones(1,7);            % límites superiores
dstep  =  delta*ones(1,7);         % paso independiente por junta (se invierte al rebotar)

% === FIGURA ÚNICA: ejes + panel de sliders ===
f = figure('Name','Control por Gestos - Sawyer','Position',[100 100 1200 600], ...
           'Color','w','NumberTitle','off');
% Panel para el robot (izquierda)
ax = axes('Parent', f, 'Units','normalized', 'Position', [0.05 0.08 0.62 0.88]);
view(ax, 45, 20); grid(ax, 'on'); box(ax, 'on');

% Dibuja el robot en el mismo AXES
axes(ax); %#ok<LAXES>
sawyer.plot(q, 'workspace', [-1000 1000 -1000 1000 -100 1200], 'delay', 0);

% Panel para sliders (derecha)
pnl = uipanel('Parent', f, 'Title','Juntas', 'FontWeight','bold', ...
              'Units','normalized', 'Position',[0.70 0.08 0.27 0.88]);

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

% === Parámetros de control de gestos ===
lastGesto    = "";
minTiempo    = 0.05;  % Espera mínima entre gestos válidos
ultimoTiempo = tic;

% === Comunicación UDP ===
u = udpport("datagram","IPV4","LocalPort",50011);
disp("Esperando gestos desde Python...");

% Cierre limpio
set(f, 'CloseRequestFcn', @(src,evt) onClose(src,evt,u));

% Publicar en base para callbacks
assignin('base','sawyer', sawyer);
assignin('base','q', q);
assignin('base','qmin', qmin);
assignin('base','qmax', qmax);

% === Loop principal ===
while ishandle(f)
    % Leer datagramas si hay
    if u.NumDatagramsAvailable > 0
        d = read(u, 1, "string");
        gesto = strtrim(d.Data);

        if ~strcmpi(gesto, lastGesto) || toc(ultimoTiempo) > minTiempo
            disp("Gesto recibido: " + gesto);
            lastGesto = gesto;
            ultimoTiempo = tic;

            switch lower(gesto)
                case "cerrada",               [q,dstep] = stepBounce(q, dstep, 1, qmin, qmax, delta);
                case "cerrada derecha",       [q,dstep] = stepBounce(q, dstep, 2, qmin, qmax, delta);
                case "cerrada izquierda",     [q,dstep] = stepBounce(q, dstep, 3, qmin, qmax, delta);
                case "abierta",               [q,dstep] = stepBounce(q, dstep, 4, qmin, qmax, delta);
                case "abierta derecha",       [q,dstep] = stepBounce(q, dstep, 5, qmin, qmax, delta);
                case "abierta izquierda",     [q,dstep] = stepBounce(q, dstep, 6, qmin, qmax, delta);
                case "derecha completa",      [q,dstep] = stepBounce(q, dstep, 7, qmin, qmax, delta);
            end

            % Actualiza sliders y robot
            for i = 1:7
                sliders(i).Value = q(i);
            end
            sawyer.animate(q);
            assignin('base','q', q);
            drawnow;
        end
    end
    pause(0.01); % lectura más natural
end

% === Callbacks y funciones auxiliares ===
function onSliderMove()
    % Si el usuario mueve cualquier slider, refleja en q y anima (clampeando a límites)
    f = gcf; % figura actual
    pnl = findobj(f, 'Type','uipanel', '-and', 'Title','Juntas');
    slds = findobj(pnl, 'Style','slider');
    % Ordenar de J1 a J7 (posiciones verticales descendentes)
    [~, idx] = sort(arrayfun(@(h) h.Position(2), slds), 'descend');
    slds = slds(idx);
    qloc = zeros(1,7);
    qmin = evalin('base','qmin'); %#ok<NASGU>
    qmax = evalin('base','qmax'); %#ok<NASGU>
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
    try, clear u; catch, end %#ok<CTCH>
    delete(src);
end

function [q, dstep] = stepBounce(q, dstep, i, qmin, qmax, base_step)
    % Avanza con el paso actual y rebota en límites cambiando el signo
    q(i) = q(i) + dstep(i);

    if q(i) >= qmax(i)
        q(i)     = qmax(i);
        dstep(i) = -abs(base_step); % rebote
    elseif q(i) <= qmin(i)
        q(i)     = qmin(i);
        dstep(i) =  abs(base_step); % rebote
    end
end

function robot = cargar_sawyer()
    % DH aproximado de Sawyer (unidades en mm)
    J1 = Revolute('d', 317,   'a', 81,   'alpha', -pi/2, 'offset', 0);
    J2 = Revolute('d', 192.5, 'a', 0,    'alpha', -pi/2, 'offset', -pi/2);
    J3 = Revolute('d', 400,   'a', 0,    'alpha', -pi/2, 'offset', 0);
    J4 = Revolute('d', 168.5, 'a', 0,    'alpha', -pi/2, 'offset', pi);
    J5 = Revolute('d', 400,   'a', 0,    'alpha', -pi/2, 'offset', 0);
    J6 = Revolute('d', 136.3, 'a', 0,    'alpha', -pi/2, 'offset', pi);
    J7 = Revolute('d', 133.75,'a', 0,    'alpha', 0,     'offset', -pi/2);
    robot = SerialLink([J1 J2 J3 J4 J5 J6 J7], 'name', 'SAWYER');
end

