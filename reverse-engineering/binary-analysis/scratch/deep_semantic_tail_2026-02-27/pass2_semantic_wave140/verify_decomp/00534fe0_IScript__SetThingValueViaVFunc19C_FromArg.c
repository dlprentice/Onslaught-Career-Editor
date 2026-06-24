/* address: 0x00534fe0 */
/* name: IScript__SetThingValueViaVFunc19C_FromArg */
/* signature: void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void * this, int param_1, void * param_2) */


void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void *this,int param_1,void *param_2)

{
  int iVar1;
  undefined4 uVar2;

  if ((*(byte *)(*(int **)((int)this + 0x10) + 0xd) & 0x10) != 0) {
    iVar1 = **(int **)((int)this + 0x10);
    uVar2 = (**(code **)(**(int **)param_1 + 0x38))();
    (**(code **)(iVar1 + 0x19c))(uVar2);
  }
  return;
}
