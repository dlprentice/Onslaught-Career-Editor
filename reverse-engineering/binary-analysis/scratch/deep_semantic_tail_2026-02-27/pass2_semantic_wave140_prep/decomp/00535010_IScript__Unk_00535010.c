/* address: 0x00535010 */
/* name: IScript__Unk_00535010 */
/* signature: void __thiscall IScript__Unk_00535010(void * this, int param_1, void * param_2) */


void __thiscall IScript__Unk_00535010(void *this,int param_1,void *param_2)

{
  int iVar1;
  void *unaff_ESI;

  if ((*(byte *)(*(int *)((int)this + 0x10) + 0x34) & 0x10) != 0) {
    iVar1 = (**(code **)(**(int **)param_1 + 0x38))();
    CEngine__Unk_004fe390(*(void **)((int)this + 0x10),iVar1,unaff_ESI);
  }
  return;
}
