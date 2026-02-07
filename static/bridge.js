// LifeCycle Bridge Page - Simple animation on load

document.addEventListener('DOMContentLoaded', () => {
    // Animate bars on load
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        bar.style.opacity = '0';
        bar.style.transform = 'translateY(20px)';

        setTimeout(() => {
            bar.style.transition = 'all 0.6s ease';
            bar.style.opacity = '1';
            bar.style.transform = 'translateY(0)';
        }, 300 + (index * 200));
    });

    // Track affiliate link clicks
    const affiliateLinks = document.querySelectorAll('.btn-primary');
    affiliateLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Optional: Send analytics event
            console.log('[LifeCycle] Affiliate link clicked');
        });
    });
});
