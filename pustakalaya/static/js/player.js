// Replace the song URLs with your local music file URLs
const musicFiles = [
    'song1.mp3',
    'song2.mp3',
    'song3.mp3'
];

let currentSongIndex = 0;
let isPlaying = false;

const audioPlayer = document.getElementById('audio-player');
const playPauseBtn = document.getElementById('play-pause-btn');
const songTitleElement = document.getElementById('song-title');
const artistNameElement = document.getElementById('artist-name');

function loadSong(index) {
    audioPlayer.src = 'music/'+ musicFiles[index];
    songTitleElement.textContent = `Song ${index + 1}`;
    artistNameElement.textContent = 'Artist Name'; // Replace with actual artist name
}

function togglePlayPause() {
    if (isPlaying) {
        audioPlayer.pause();
    } else {
        audioPlayer.play();
    }
    isPlaying = !isPlaying;
    playPauseBtn.textContent = isPlaying ? 'pause_circle' : 'play_circle';
}

function playNextSong() {
    currentSongIndex = (currentSongIndex + 1) % musicFiles.length;
    loadSong(currentSongIndex);
    if (isPlaying) {
        audioPlayer.play();
    }
}

function playPreviousSong() {
    currentSongIndex = (currentSongIndex - 1 + musicFiles.length) % musicFiles.length;
    loadSong(currentSongIndex);
    if (isPlaying) {
        audioPlayer.play();
    }
}

// Event listeners
playPauseBtn.addEventListener('click', togglePlayPause);
document.getElementById('next-btn').addEventListener('click', playNextSong);
document.getElementById('previous-btn').addEventListener('click', playPreviousSong);

// // Initial setup
// loadSong(currentSongIndex);
