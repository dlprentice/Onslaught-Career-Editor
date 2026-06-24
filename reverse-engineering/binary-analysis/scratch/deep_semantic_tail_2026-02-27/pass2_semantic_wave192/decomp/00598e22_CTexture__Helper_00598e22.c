/* address: 0x00598e22 */
/* name: CTexture__Helper_00598e22 */
/* signature: void __fastcall CTexture__Helper_00598e22(void * param_1) */


void __fastcall CTexture__Helper_00598e22(void *param_1)

{
  int *piVar1;

  *(undefined ***)param_1 = &PTR_CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag_005ef270;
  if ((*(int *)((int)param_1 + 0x10) == 5) &&
     (piVar1 = *(int **)((int)param_1 + 0x18), piVar1 != (int *)0x0)) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)((int)param_1 + 0x18) = 0;
  }
  if ((*(int *)((int)param_1 + 0x10) == 4) &&
     (*(undefined4 **)((int)param_1 + 0x18) != (undefined4 *)0x0)) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x18))(1);
  }
  CDXTexture__ReleaseNodePayloadChain(param_1);
  return;
}
