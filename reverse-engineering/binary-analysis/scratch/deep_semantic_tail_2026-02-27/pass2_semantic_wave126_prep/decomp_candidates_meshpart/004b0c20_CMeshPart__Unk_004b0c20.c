/* address: 0x004b0c20 */
/* name: CMeshPart__Unk_004b0c20 */
/* signature: void __thiscall CMeshPart__Unk_004b0c20(void * this, int param_1, void * param_2) */


void __thiscall CMeshPart__Unk_004b0c20(void *this,int param_1,void *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;

  uVar1 = *(undefined4 *)((int)this + 0x28);
  uVar2 = *(undefined4 *)((int)this + 0x18);
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 8);
  *(undefined4 *)(param_1 + 4) = uVar2;
  *(undefined4 *)(param_1 + 8) = uVar1;
  return;
}
