/* address: 0x00535040 */
/* name: IScript__SetThingValueViaEngineHelper4FE3F0_FromArg */
/* signature: void __thiscall IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void * this, int param_1, void * param_2) */


void __thiscall
IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void *this,int param_1,void *param_2)

{
  int iVar1;
  void *unaff_ESI;

  if ((*(byte *)(*(int *)((int)this + 0x10) + 0x34) & 0x10) != 0) {
    iVar1 = (**(code **)(**(int **)param_1 + 0x38))();
    CEngine__Unk_004fe3f0(*(void **)((int)this + 0x10),iVar1,unaff_ESI);
  }
  return;
}
