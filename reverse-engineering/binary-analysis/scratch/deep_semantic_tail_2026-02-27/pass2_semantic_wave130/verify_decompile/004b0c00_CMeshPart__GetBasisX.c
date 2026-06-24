/* address: 0x004b0c00 */
/* name: CMeshPart__GetBasisX */
/* signature: void __thiscall CMeshPart__GetBasisX(void * this, int param_1, void * param_2) */


void __thiscall CMeshPart__GetBasisX(void *this,int param_1,void *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;

  uVar1 = *(undefined4 *)((int)this + 0x24);
  uVar2 = *(undefined4 *)((int)this + 0x14);
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 4);
  *(undefined4 *)(param_1 + 4) = uVar2;
  *(undefined4 *)(param_1 + 8) = uVar1;
  return;
}
