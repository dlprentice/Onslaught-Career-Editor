/* address: 0x004aa3f0 */
/* name: CMesh__Unk_004aa3f0 */
/* signature: void __thiscall CMesh__Unk_004aa3f0(void * this, void * param_1, void * param_2) */


void __thiscall CMesh__Unk_004aa3f0(void *this,void *param_1,void *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;

  uVar1 = *(undefined4 *)((int)this + 0x20);
  uVar2 = *(undefined4 *)((int)this + 0x10);
  *(undefined4 *)param_1 = *(undefined4 *)this;
  *(undefined4 *)((int)param_1 + 4) = uVar2;
  *(undefined4 *)((int)param_1 + 8) = uVar1;
  return;
}
