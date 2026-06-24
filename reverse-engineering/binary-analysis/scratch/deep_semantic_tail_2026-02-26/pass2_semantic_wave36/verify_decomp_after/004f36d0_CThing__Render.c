/* address: 0x004f36d0 */
/* name: CThing__Render */
/* signature: void __thiscall CThing__Render(void * this, int param_1, uint param_2) */


void __thiscall CThing__Render(void *this,int param_1,uint param_2)

{
  ushort uVar1;

  uVar1 = *(ushort *)((int)this + 0x2c);
  if ((uVar1 & 0x10) == 0) {
    if ((uVar1 & 0x20) != 0) {
      param_1 = param_1 | 2;
    }
    if ((*(int **)((int)this + 0x30) != (int *)0x0) && ((uVar1 & 8) == 0)) {
      (**(code **)(**(int **)((int)this + 0x30) + 8))(param_1);
      if ((DAT_0089ce54 & 0x20) != 0) {
        CThing__DrawDebugCuboid(this);
      }
    }
  }
  return;
}
