/* address: 0x00482050 */
/* name: CDXEngine__SwapPendingHudRenderComponent */
/* signature: void __fastcall CDXEngine__SwapPendingHudRenderComponent(int param_1) */


void __fastcall CDXEngine__SwapPendingHudRenderComponent(int param_1)

{
  undefined4 uVar1;

  if (*(int *)(param_1 + 0x200) != 0) {
    if (*(int *)(param_1 + 0x1fc) != 0) {
      (**(code **)(*(int *)(*(int *)(param_1 + 0x1fc) + 4) + 4))(1);
    }
    uVar1 = *(undefined4 *)(param_1 + 0x200);
    *(undefined4 *)(param_1 + 0x200) = 0;
    *(undefined4 *)(param_1 + 0x1fc) = uVar1;
  }
  return;
}
