/* address: 0x00544770 */
/* name: CDXLandscape__Helper_00544770 */
/* signature: void __fastcall CDXLandscape__Helper_00544770(void * param_1) */


void __fastcall CDXLandscape__Helper_00544770(void *param_1)

{
  int iVar1;

  if (*(undefined4 **)param_1 != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)param_1)(3);
    *(undefined4 *)param_1 = 0;
  }
  iVar1 = *(int *)((int)param_1 + 8);
  if (iVar1 != 0) {
    CDXLandscape__Helper_0055db0a(iVar1,0xc,*(int *)(iVar1 + -4),CDXLandscape__Helper_005447d0);
    OID__FreeObject((void *)(iVar1 + -4));
    *(undefined4 *)((int)param_1 + 8) = 0;
  }
  if (*(void **)((int)param_1 + 4) != (void *)0x0) {
    OID__FreeObject(*(void **)((int)param_1 + 4));
    *(undefined4 *)((int)param_1 + 4) = 0;
  }
  return;
}
