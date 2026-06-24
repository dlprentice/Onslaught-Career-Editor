/* address: 0x005b1db0 */
/* name: CDXTexture__Helper_005b1db0 */
/* signature: void __stdcall CDXTexture__Helper_005b1db0(void * param_1, int param_2, void * param_3) */


void CDXTexture__Helper_005b1db0(void *param_1,int param_2,void *param_3)

{
  undefined4 uVar1;

  if (param_3 != (void *)0x0) {
    *(undefined4 *)param_3 = *(undefined4 *)((int)param_1 + 0x3c);
  }
  if ((*(int *)param_1 == 4) || (*(int *)param_1 == 5)) {
    (**(code **)(param_2 + 0x24))
              (*(undefined4 *)(param_2 + 0x28),*(undefined4 *)((int)param_1 + 0xc));
  }
  if (*(int *)param_1 == 6) {
    CDXTexture__InvokeReleaseCallback(*(int *)((int)param_1 + 4),param_2);
  }
  *(undefined4 *)((int)param_1 + 0x34) = *(undefined4 *)((int)param_1 + 0x28);
  *(undefined4 *)((int)param_1 + 0x30) = *(undefined4 *)((int)param_1 + 0x28);
  *(undefined4 *)param_1 = 0;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  if (*(code **)((int)param_1 + 0x38) != (code *)0x0) {
    uVar1 = (**(code **)((int)param_1 + 0x38))(0,0,0);
    *(undefined4 *)((int)param_1 + 0x3c) = uVar1;
    *(undefined4 *)(param_2 + 0x30) = uVar1;
  }
  return;
}
