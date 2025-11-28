classdef ToggleValue < matlab.System
    % Toggles output between 4.5 and 1 every X seconds, where X is the input
    
    properties (Access = private)
        lastSwitchTime      % time of last toggle
        currentValue        % current output value
    end

    methods (Access = protected)

        function setupImpl(obj)
            % Initialize state at start of simulation
            obj.lastSwitchTime = 0;
            obj.currentValue = 4.5;   % starting output
        end

        function y = stepImpl(obj, togglePeriod)
            % togglePeriod: input specifying X seconds (scalar)
            
            % Protect against zero or negative input
            if togglePeriod <= 0
                togglePeriod = 1; % default to 1 second
            end

            % Current simulation time
            t = getCurrentTime(obj);

            % Toggle when time difference exceeds togglePeriod
            if t - obj.lastSwitchTime >= togglePeriod
                if obj.currentValue == 4.5
                    obj.currentValue = 1;
                else
                    obj.currentValue = 4.5;
                end
                obj.lastSwitchTime = t;  % update timestamp
            end

            % Output
            y = obj.currentValue;
        end

        % Input port specifications
        function num = getNumInputsImpl(~)
            num = 1;
        end

        function validateInputsImpl(~, togglePeriod)
            % Ensure numeric scalar
            if ~isscalar(togglePeriod)
                error("Input toggle period must be a scalar.");
            end
        end
        
        % Output is scalar double
        function outSize = getOutputSizeImpl(~)
            outSize = [1 1];
        end
        
        function outType = getOutputDataTypeImpl(~)
            outType = "double";
        end
        
        function cplx = isOutputComplexImpl(~)
            cplx = false;
        end
        
        function fixed = isOutputFixedSizeImpl(~)
            fixed = true;
        end
    end
end