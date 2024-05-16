function confirmDelete(postTitle, postID) {
    if (confirm(`Tem certeza que deseja deletar o post "${postTitle}"?`)) {
        window.location.href = `/posts/deletar/${postID}`;
    }
}
