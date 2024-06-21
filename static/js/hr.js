$(document).ready(function() {
    $('#showAddEmployeeFormBtn').click(function() {
        $('.form-container').hide();
        $('#addEmployeeFormContainer').show();
    });

    $('#showUpdateEmployeeFormBtn').click(function() {
        $('.form-container').hide();
        $('#updateEmployeeFormContainer').show();
    });

    $('#showUpdateSalaryFormBtn').click(function() {
        $('.form-container').hide();
        $('#updateSalaryFormContainer').show();
    });

    $('#showChangePasswordFormBtn').click(function() {
        $('.form-container').hide();
        $('#changePasswordFormContainer').show();
    });

    $('#showDeleteEmployeeFormBtn').click(function() {
        $('.form-container').hide();
        $('#deleteEmployeeFormContainer').show();
    });

    $('#addEmployeeForm').submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/add_employee',
            data: $(this).serialize(),
            success: function (response) {
                alert('Employee added successfully');
                location.reload();
            },
            error: function (error) {
                alert('Failed to add employee');
            }
        });
    });

    $('#updateEmployeeForm').submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/update_employee',
            data: $(this).serialize(),
            success: function (response) {
                alert('Employee updated successfully');
                location.reload();
            },
            error: function (error) {
                alert('Failed to update employee');
            }
        });
    });

    function calculateTotalSalary() {
        const basicSalary = parseFloat($('#basic_salary').val()) || 0;
        const performanceBonus = parseFloat($('#performance_bonus').val()) || 0;
        const overtimePay = parseFloat($('#overtime_pay').val()) || 0;
        const allowances = parseFloat($('#allowances').val()) || 0;
        const deductions = parseFloat($('#deductions').val()) || 0;

        const totalSalary = basicSalary + performanceBonus + overtimePay + allowances - deductions;
        $('#total_salary').val(totalSalary.toFixed(2));
    }

    $('#basic_salary, #performance_bonus, #overtime_pay, #allowances, #deductions').on('input', calculateTotalSalary);

    $('#updateSalaryForm').submit(function (event) {
        event.preventDefault();
        calculateTotalSalary();
        $.ajax({
            type: 'POST',
            url: '/update_salary',
            data: $(this).serialize(),
            success: function (response) {
                alert('Salary updated successfully');
                location.reload();
            },
            error: function (error) {
                alert('Failed to update salary');
            }
        });
    });

    $('#changePasswordForm').submit(function (event) {
        event.preventDefault();
        const currentPassword = $('#current_password').val();
        const newPassword = $('#new_password').val();
        const confirmNewPassword = $('#confirm_new_password').val();

        if (newPassword !== confirmNewPassword) {
            $('#alert').removeClass('success').addClass('error').text('The new passwords entered do not match.').show();
            return;
        }

        $.ajax({
            type: 'POST',
            url: '/change_password',
            data: {
                current_password: currentPassword,
                new_password: newPassword,
                confirm_new_password: confirmNewPassword
            },
            success: function (response) {
                if (response.correctCurrentPassword) {
                    if (response.success) {
                        $('#alert').removeClass('error').addClass('success').text('Password successfully changed.').show();
                    } else {
                        $('#alert').removeClass('success').addClass('error').text('Password change failed.').show();
                    }
                } else {
                    $('#alert').removeClass('error').addClass('success').text('Password successfully changed.').show();
                }
            },
            error: function (error) {
                $('#alert').removeClass('success').addClass('error').text('Password change failed.').show();
            }
        });
    });

    $('#deleteEmployeeForm').submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/delete_employee',
            data: $(this).serialize(),
            success: function (response) {
                alert('Employee deleted successfully');
                location.reload();
            },
            error: function (error) {
                alert('Failed to delete employee');
            }
        });
    });

    $('th[data-key]').click(function() {
        const th = $(this);
        const key = th.data('key');
        const order = th.data('order') || 'asc';
        const rows = $('#employeeTable tbody tr').get();

        rows.sort(function(a, b) {
            const A = $(a).children('td').eq($('th[data-key="' + key + '"]').index()).text().toUpperCase();
            const B = $(b).children('td').eq($('th[data-key="' + key + '"]').index()).text().toUpperCase();

            if (A < B) {
                return order === 'asc' ? -1 : 1;
            }
            if (A > B) {
                return order === 'asc' ? 1 : -1;
            }
            return 0;
        });

        $.each(rows, function(index, row) {
            $('#employeeTable').children('tbody').append(row);
        });

        $('th[data-key]').not(th).removeClass('sort-asc sort-desc').data('order', '');

        if (order === 'asc') {
            th.removeClass('sort-asc').addClass('sort-desc').data('order', 'desc');
        } else {
            th.removeClass('sort-desc').addClass('sort-asc').data('order', 'asc');
        }
    });


    $('#employeeTable tbody tr').click(function() {
            var employeeId = $(this).find('td:first').text();
            // window.location.href = 'http://127.0.0.1:1833/employee_salary?employee_id=' + employeeId;
            window.location.href = 'http://172.25.203.200:1833/employee_salary?employee_id=' + employeeId;
        });

    // listItem.click(function() {
    //     var employeeId = employee.id;
    //     var url = 'http://127.0.0.1:1833/employee_salary?employee_id=' + employeeId;
    //
    //     // 检查第一个链接是否存在
    //     var firstImage = document.getElementsByClassName("carousel")[0].getElementsByTagName("img")[0];
    //     if (!firstImage || !firstImage.src) {
    //         // 如果第一个链接不存在或找不到页面，则跳转到备用链接
    //         url = 'http://172.25.203.200:1833/employee_salary?employee_id=' + employeeId;
    //     }
    //
    //     window.location.href = url;
    // });

        $('#showFilterFormBtn').click(function() {
            $('.form-container').hide();
            $('#filterFormContainer').show();
        });

        $('#filterForm').submit(function (event) {
            event.preventDefault();
            const position = $('#filter_position').val();
            const educationalBackground = $('#filter_educational_background').val();
            const employmentStatus = $('#filter_employment_status').val();

            $.ajax({
                type: 'POST',
                url: '/filter_employees',
                data: {
                    position: position,
                    educational_background: educationalBackground,
                    employment_status: employmentStatus
                },
                success: function (response) {
                    $('#filterResult').html('<h3>Filtered Employees</h3>');
                    $('#filterResult').append('<p>Total: ' + response.total + '</p>');
                    const employeeList = $('<ul></ul>');
                    response.employees.forEach(function(employee) {
                        employeeList.append('<li>' + employee.id + ': ' + employee.name + '</li>');
                    });
                    $('#filterResult').append(employeeList);
                },
                error: function (error) {
                    alert('Failed to filter employees');
                }
            });
        });

        const rowsPerPage = 10;
        let currentPage = 1;
        const $table = $('#employeeTable');
        const $rows = $table.find('tbody tr');
        const totalPages = Math.ceil($rows.length / rowsPerPage);
        const $pageNumberSelect = $('#pageNumber');

        function showPage(page) {
            $rows.hide();
            $rows.slice((page - 1) * rowsPerPage, page * rowsPerPage).show();
            $pageNumberSelect.val(page);
        }

        function updateButtons() {
            $('#prevPage').prop('disabled', currentPage === 1);
            $('#nextPage').prop('disabled', currentPage === totalPages);
        }

        function populatePageNumbers() {
            $pageNumberSelect.empty();
            for (let i = 1; i <= totalPages; i++) {
                $pageNumberSelect.append(`<option value="${i}">${i}</option>`);
            }
        }

        $('#prevPage').click(function() {
            if (currentPage > 1) {
                currentPage--;
                showPage(currentPage);
                updateButtons();
            }
        });

        $('#nextPage').click(function() {
            if (currentPage < totalPages) {
                currentPage++;
                showPage(currentPage);
                updateButtons();
            }
        });

        $pageNumberSelect.change(function() {
            currentPage = parseInt($(this).val());
            showPage(currentPage);
            updateButtons();
        });

        // Initial setup
        populatePageNumbers();
        showPage(currentPage);
        updateButtons();



// Add the filter form event handler
    $('#filterForm').submit(function(event) {
    event.preventDefault();
    const position = $('#filter_position').val();
    const educationalBackground = $('#filter_educational_background').val();
    const employmentStatus = $('#filter_employment_status').val();

    $.ajax({
        type: 'POST',
        url: '/filter_employees',
        data: {
            position: position,
            educational_background: educationalBackground,
            employment_status: employmentStatus
        },
        success: function(response) {
            $('#filterResult').html('<h3>Filtered Employees</h3>');
            $('#filterResult').append('<p>Total: ' + response.total + '</p>');

            if (response.total > 0) {
                const employeeList = $('<ul></ul>').css({
                    'list-style': 'none',
                    'padding': '0',
                    'margin': '0',
                    'border-top': '1px solid #ddd'
                });

                response.employees.forEach(function(employee) {
                    const listItem = $('<li></li>').css({
                        'border': '1px solid #ddd',
                        'margin': '10px 0',
                        'padding': '10px',
                        'border-radius': '5px',
                        'background-color': '#f9f9f9',
                        'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                        'transition': 'background-color 0.3s ease',
                        'cursor': 'pointer'
                    });

                    listItem.hover(function() {
                        $(this).css('background-color', '#e9ecef');
                    }, function() {
                        $(this).css('background-color', '#f9f9f9');
                    });

                    listItem.click(function() {
                         window.location.href = 'http://127.0.0.1:1833/employee_salary?employee_id=' + employee.id;
//                        window.location.href = 'http://172.25.203.200:1833/employee_salary?employee_id=' + employeeId;
                    });

                    listItem.append('<strong>ID:</strong> ' + employee.id + '<br>');
                    listItem.append('<strong>Name:</strong> ' + employee.name + '<br>');
                    listItem.append('<strong>Position:</strong> ' + employee.position + '<br>');
                    listItem.append('<strong>Educational Background:</strong> ' + employee.educational_background + '<br>');
                    listItem.append('<strong>Employment Status:</strong> ' + employee.employment_status);

                    employeeList.append(listItem);
                });

                $('#filterResult').append(employeeList);
            } else {
                $('#filterResult').append('<p>No employees match the filter criteria.</p>');
            }
        },
        error: function(error) {
            alert('Failed to filter employees');
        }
    });
});
});
