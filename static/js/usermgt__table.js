
load_table()

function load_table() {
    $.ajax({
        url: "load_user_table/", 
        method: "GET",
        success: function(data) {

            data.users.forEach(function(user) {
                var userHtml = `
                    <div class="grid grid-cols-5 gap-4 text-sm border-light py-2 items-center">
                        <img src="/static/img/default_img/${user.image_filename}" alt="" class="rounded-md w-[1.7rem] h-[1.7rem] col-span-1">
                        <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${user.firstname + " " + user.lastname}</div>
                        <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${user.username}</div>
                        <div class="col-span-1 whitespace-nowrap">${user.status}</div>
                        <div class="flex col-span-1">
                            <button id="${user.id}" class="text-white bg-blue-500 px-4 py-2 rounded-md text-white bg-red-400 hover:bg-red-300">
                            Delete
                            </button>
                        </div>
                    </div>
                `;
             
    
                $("#span__users").append(userHtml);
            });
        }
    })
}

$("#search__user").keyup(function(){
    search_table() 
})


function search_table () {
    if($("#search__user").val().length > 0) {
        var search = $("#search__user").val()
        $("#span__users").empty();
        $.ajax({
            url: "search_user_table/", 
            method: "POST",
            data: {'search': search},
            success: function(data) {
                
                if (data.users !== 'none') {
                    if (Array.isArray(data.users)) {
                        // If data.users is an array
                        data.users.forEach(function(user) {
                            var userHtml = `
                                <div class="grid grid-cols-5 gap-4 text-sm border-light py-2 items-center">
                                    <img src="/static/img/default_img/${user.image_filename}" alt="" class="rounded-md w-[1.7rem] h-[1.7rem] col-span-1">
                                    <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${user.firstname + " " + user.lastname}</div>
                                    <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${user.username}</div>
                                    <div class="col-span-1 whitespace-nowrap">${user.status}</div>
                                    <div class="flex col-span-1">
                                        <button id="${user.id}" class="text-white bg-blue-500 px-4 py-2 rounded-md text-white bg-red-400 hover:bg-red-300">
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            `;
                            $("#span__users").html(userHtml);
                        });
                    } else {
                        // If data.users is a single object
                        var userHtml = `
                            <div class="grid grid-cols-5 gap-4 text-sm border-light py-2 items-center">
                                <img src="/static/img/default_img/${data.users.image_filename}" alt="" class="rounded-md w-[1.7rem] h-[1.7rem] col-span-1">
                                <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${data.users.firstname + " " + data.users.lastname}</div>
                                <div class="col-span-1 overflow-x-auto whitespace-nowrap w-3/5">${data.users.username}</div>
                                <div class="col-span-1 whitespace-nowrap">${data.users.status}</div>
                                <div class="flex col-span-1">
                                    <button id="${data.users.id}" class="text-white bg-blue-500 px-4 py-2 rounded-md text-white bg-red-400 hover:bg-red-300">
                                        Delete
                                    </button>
                                </div>
                            </div>
                        `;
                        $("#span__users").html(userHtml);
                    }
                }
                
            }
        })

    }else{
        load_table()
    }

}