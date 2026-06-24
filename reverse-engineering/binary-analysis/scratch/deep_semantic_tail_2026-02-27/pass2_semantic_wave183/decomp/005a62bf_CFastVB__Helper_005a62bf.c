/* address: 0x005a62bf */
/* name: CFastVB__Helper_005a62bf */
/* signature: void __cdecl CFastVB__Helper_005a62bf(void * param_1) */


void __cdecl CFastVB__Helper_005a62bf(void *param_1)

{
  ulonglong uVar1;

  uVar1 = (ulonglong)DAT_005ef0f0;
  *(ulonglong *)param_1 = uVar1;
  *(undefined8 *)((int)param_1 + 8) = 0;
  *(undefined8 *)((int)param_1 + 0x18) = 0;
  *(undefined8 *)((int)param_1 + 0x20) = 0;
  *(ulonglong *)((int)param_1 + 0x28) = uVar1;
  *(undefined8 *)((int)param_1 + 0x30) = 0;
  *(ulonglong *)((int)param_1 + 0x10) = uVar1 << 0x20;
  *(ulonglong *)((int)param_1 + 0x38) = uVar1 << 0x20;
  FastExitMediaState();
  return;
}
