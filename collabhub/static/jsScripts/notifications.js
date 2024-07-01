
let notifications = document.querySelector(".notifications");
let toasts = notifications.children

window.addEventListener("DOMContentLoaded", () => {
    for (let i = 0; i < toasts.length; i++) {
        const toast = toasts[i];
        toast.classList.remove("toast-nondisplay");
        toast.classList.add("toast-display");
        setTimeout(() => {
            try {
                toast.remove();
            } catch {
                console.log("Already removed");
            }
        }, 5000)
        toast.children[2].addEventListener("click", () => {
            toast.remove();
        })
    }
})

