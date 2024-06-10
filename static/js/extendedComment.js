
function handleComments() {
const comments = document.querySelectorAll('p[id^="comment-"]');
comments.forEach(comment => {
    const commentText = comment.childNodes[0].nodeValue.trim();
    if (commentText.length > 45) {
    const shortText = commentText.substring(0, 35) + "...";
    const moreLink = document.createElement('a');
    moreLink.href = 'javascript:void(0)';
    moreLink.innerText = 'Read More';
    moreLink.onclick = function() {
        showModal(commentText);
    };
    comment.childNodes[0].nodeValue = shortText;
    comment.appendChild(moreLink);
    }
});
}

function showModal(text) {
const modal = document.getElementById('commentModal');
const modalContent = document.getElementById('modalContent');
modalContent.innerText = text;
modal.style.display = 'block';
}

function closeModal() {
const modal = document.getElementById('commentModal');
modal.style.display = 'none';
}

// Execute the function once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', handleComments);

