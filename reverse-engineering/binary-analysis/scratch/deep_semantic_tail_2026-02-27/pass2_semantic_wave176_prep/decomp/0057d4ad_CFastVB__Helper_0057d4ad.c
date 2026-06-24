/* address: 0x0057d4ad */
/* name: CFastVB__Helper_0057d4ad */
/* signature: void __fastcall CFastVB__Helper_0057d4ad(void * param_1) */


void __fastcall CFastVB__Helper_0057d4ad(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)param_1;
  (*(code *)PTR_CDXTexture__InitMmxDispatchAndRun_00657978)
            (*(undefined4 *)(*(int *)((int)param_1 + 4) + 0x20),*(undefined4 *)(iVar1 + 0x20),
             *(undefined4 *)(iVar1 + 0x1060),*(undefined4 *)(iVar1 + 0x1064),
             *(undefined4 *)(iVar1 + 0x1058),*(undefined4 *)(*(int *)((int)param_1 + 4) + 0x1058));
  return;
}
