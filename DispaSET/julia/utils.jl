
function cond(s, expr)
        if length(s)>0
                return eval(Meta.parse(expr))
        else
                return 0
        end
end



function start_value_parameter(h, parameter, parameter_inital, set)
        """
        only works for 1d set
        """

        if h==1
                parameter_inital[set]
        else
                parameter[set, h-1]
        end
end


function if_lp(expr)
        if LPFormulation==1
                return expr
        else
                return 0
        end
end

macro lp_formulation(ex)
        if LPFormulation==1
                return :($ex)
        end
end
