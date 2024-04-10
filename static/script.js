const boxes = document.querySelectorAll(".box");
const images = document.querySelectorAll(".image");

boxes.forEach((box) => {
    box.addEventListener("dragover", (e) => {
        e.preventDefault();
        box.classList.add("hovered");
    });
    box.addEventListener("dragleave", () => {
        box.classList.remove("hovered");
    });
    box.addEventListener("drop", () => {
        box.appendChild(images[0]);
        box.classList.remove("hovered");
    });
});

const selectElement = document.getElementById("trigger");
const modal = document.getElementById("myModal");
const closeBtn = document.querySelector(".close");
const appSelectElement = document.getElementById("appSelect");
const actionSelectElement = document.getElementById("actionSelect");
const emailFields = document.getElementById("emailFields");

selectElement.addEventListener("change", () => {
    const selectedValue = selectElement.value;
    localStorage.setItem("selectedTrigger", selectedValue);
    modal.style.display = "none";
    if (selectedValue === "manual") {
        images.forEach((img) => {
            img.style.backgroundImage = 'url("/static/images/click.png")';
        });
    }
});

images.forEach((img) => {
    img.addEventListener("click", () => {
        modal.style.display = "block";
    });
});

closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
});

document.addEventListener("DOMContentLoaded", () => {
    const storedValue = localStorage.getItem("selectedTrigger");
    if (storedValue) {
        selectElement.value = storedValue;
    }
});

const actionElement = document.getElementById("action");

actionElement.addEventListener("change", () => {
    const selectedAction = actionElement.value;
    if (selectedAction === "action_app") {
        appSelectElement.style.display = "block";
        actionSelectElement.style.display = "none";
        emailFields.style.display = "none";
        modal.style.display = "none";
    } else {
        appSelectElement.style.display = "none";
        actionSelectElement.style.display = "none";
        emailFields.style.display = "none";
        modal.style.display = "none";
        if (selectedAction === "sendEmail" && appSelectElement.value === "gmail") {
            emailFields.style.display = "block";
            modal.style.display = "block";
        }
    }
});

appSelectElement.addEventListener("change", () => {
    const selectedApp = appSelectElement.value;
    if (selectedApp === "gmail") {
        actionSelectElement.style.display = "block";
    } else {
        actionSelectElement.style.display = "none";
    }
});

actionSelectElement.addEventListener("change", () => {
    const selectedAction = actionSelectElement.value;
    if (selectedAction === "sendEmail") {
        emailFields.style.display = "block";
    } else {
        emailFields.style.display = "none";
    }
});
const saveButton = document.getElementById("saveButton");
saveButton.addEventListener("click", () => {
    const formData = new FormData(document.getElementById("myForm"));
    console.log("Form data:", formData);
    const testWorkflowButton = document.getElementById("testWorkflowButton");
    testWorkflowButton.style.display = "block";
    modal.style.display = "none";
});

const testWorkflowButton = document.getElementById("testWorkflowButton");
testWorkflowButton.addEventListener("click", () => {
    fetch("/automation", {
        method: "POST",
        body: JSON.stringify({}), 
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => {
        console.log("Test Workflow response:", response);
    })
    .catch(error => {
        console.error("Test Workflow error:", error);
    });
});
