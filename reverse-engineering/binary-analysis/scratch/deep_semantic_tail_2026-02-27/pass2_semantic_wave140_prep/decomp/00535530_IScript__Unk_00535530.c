/* address: 0x00535530 */
/* name: IScript__Unk_00535530 */
/* signature: void __thiscall IScript__Unk_00535530(void * this, int param_1, void * param_2) */


void __thiscall IScript__Unk_00535530(void *this,int param_1,void *param_2)

{
  int iVar1;
  float10 fVar2;

  if ((*(byte *)(*(int **)((int)this + 0x10) + 0xd) & 0x10) != 0) {
    iVar1 = **(int **)((int)this + 0x10);
    fVar2 = (float10)(**(code **)(**(int **)param_1 + 0x34))();
    (**(code **)(iVar1 + 0x1c8))((float)fVar2);
  }
  return;
}
