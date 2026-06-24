/* address: 0x0048f1e0 */
/* name: CUnitAI__Unk_0048f1e0 */
/* signature: void __thiscall CUnitAI__Unk_0048f1e0(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__Unk_0048f1e0(void *this,int param_1,int param_2)

{
  int iVar1;

  *(int *)((int)this + 0x44) = param_1;
  iVar1 = (param_1 + 1) * (param_1 + 1);
  *(undefined4 *)((int)this + 0x30) = 0;
  *(undefined4 *)((int)this + 0x2c) = 0;
  *(undefined2 *)((int)this + 0x3c) = 0xffff;
  *(undefined4 *)((int)this + 0x40) = 0;
  *(int *)((int)this + 0x38) = iVar1;
  CVBuffer__Create(iVar1,0x14,0x102);
  return;
}
