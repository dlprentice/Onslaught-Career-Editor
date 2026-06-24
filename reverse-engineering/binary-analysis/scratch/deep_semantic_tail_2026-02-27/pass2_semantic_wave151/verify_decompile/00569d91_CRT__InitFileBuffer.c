/* address: 0x00569d91 */
/* name: CRT__InitFileBuffer */
/* signature: void __cdecl CRT__InitFileBuffer(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CRT__InitFileBuffer(void *param_1)

{
  void *pvVar1;

  _DAT_009d0908 = _DAT_009d0908 + 1;
  pvVar1 = _malloc(0x1000);
  *(void **)((int)param_1 + 8) = pvVar1;
  if (pvVar1 == (void *)0x0) {
    *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) | 4;
    *(int *)((int)param_1 + 8) = (int)param_1 + 0x14;
    *(undefined4 *)((int)param_1 + 0x18) = 2;
  }
  else {
    *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) | 8;
    *(undefined4 *)((int)param_1 + 0x18) = 0x1000;
  }
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)param_1 = *(undefined4 *)((int)param_1 + 8);
  return;
}
