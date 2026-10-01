"""User-visible page turning for lists; never reveal content through DOM mutations."""
def reveal(page, locator):
    page.wait_for_function('()=>!window.requestIdleCallback || document.readyState === "complete"')
    page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    if locator.is_visible():
        return locator
    book_id=locator.evaluate('e=>e.closest(".folio")?.id')
    if not book_id and locator.get_attribute('data-k') is not None:
        target=int(locator.get_attribute('data-k'))//5
        while page.evaluate('ROUTE_CHAPTER')!=target:
            direction=0 if page.evaluate('ROUTE_CHAPTER')>target else 1
            page.locator('#chapterTurns button').nth(direction).click()
        return locator
    if not book_id:
        raise AssertionError('Target has no visible screen or page: '+str(locator))
    book=page.locator('#'+book_id)
    previous=book.locator(':scope > .folioNav button').first
    while previous.is_enabled():
        previous.click()
    for _ in range(30):
        if locator.is_visible():
            return locator
        following=book.locator(':scope > .folioNav button').last
        assert following.is_enabled(), 'No reachable page for '+str(locator)
        following.click()
    raise AssertionError('Page navigation did not reach '+str(locator))
