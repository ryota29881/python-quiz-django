document.addEventListener("DOMContentLoaded", function () {
    const groups = {
        rule_assignment: ["assignment_variable", "assignment_value"],
        rule_print: ["print_variable"],
        rule_for_loop: ["for_use_range", "for_target", "for_print_variable"],
        rule_while_loop: [],
        rule_if_statement: [],
        rule_function: ["function_name", "function_arg_count", "function_has_return"],
        rule_class: ["class_name"],
        rule_list_assignment: ["list_variable", "list_length"],
        rule_dict_assignment: ["dict_variable"],
        rule_compare: ["compare_operator"],
    };

    function row(id) {
        return document.getElementById("id_" + id)?.closest(".form-row");
    }

    function update() {
        Object.entries(groups).forEach(([checkboxId, fields]) => {
            const checkbox = document.getElementById("id_" + checkboxId);
            const checked = checkbox ? checkbox.checked : false;

            fields.forEach((fieldId) => {
                const target = row(fieldId);
                if (target) {
                    target.style.display = checked ? "" : "none";
                }
            });
        });
    }

    Object.keys(groups).forEach((checkboxId) => {
        const checkbox = document.getElementById("id_" + checkboxId);
        if (checkbox) {
            checkbox.addEventListener("change", update);
        }
    });

    update();
});
