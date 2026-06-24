/* address: 0x004a3be0 */
/* name: CMenuItemDropdown__RenderOrQueueDeferred */
/* signature: void __thiscall CMenuItemDropdown__RenderOrQueueDeferred(void * this, float x, float y, int interactive) */


void __thiscall CMenuItemDropdown__RenderOrQueueDeferred(void *this,float x,float y,int interactive)

{
  if ((interactive != 0) && (DAT_0070486c == (void *)0x0)) {
    DAT_00704874 = x;
    DAT_00704870 = y;
    DAT_0070486c = this;
    return;
  }
  CMenuItemDropdown__Render(x,y,0);
  return;
}
