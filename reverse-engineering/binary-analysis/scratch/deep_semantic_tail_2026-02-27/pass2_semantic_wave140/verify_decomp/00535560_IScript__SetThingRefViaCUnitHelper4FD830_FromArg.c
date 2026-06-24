/* address: 0x00535560 */
/* name: IScript__SetThingRefViaCUnitHelper4FD830_FromArg */
/* signature: void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void * this, int param_1, void * param_2) */


void __thiscall
IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void *this,int param_1,void *param_2)

{
  void *pvVar1;
  int unaff_ESI;

  if ((*(byte *)(*(int *)((int)this + 0x10) + 0x34) & 0x10) != 0) {
    pvVar1 = (void *)(**(code **)(**(int **)param_1 + 0x30))();
    CUnit__Unk_004fd830(*(void **)((int)this + 0x10),pvVar1,unaff_ESI);
  }
  return;
}
