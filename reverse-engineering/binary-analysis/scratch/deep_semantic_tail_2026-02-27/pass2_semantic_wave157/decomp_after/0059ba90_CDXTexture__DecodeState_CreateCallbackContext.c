/* address: 0x0059ba90 */
/* name: CDXTexture__DecodeState_CreateCallbackContext */
/* signature: void __stdcall CDXTexture__DecodeState_CreateCallbackContext(int param_1) */


void CDXTexture__DecodeState_CreateCallbackContext(int param_1)

{
  undefined4 *puVar1;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,0,0x1c);
  *(undefined4 **)(param_1 + 0x1b8) = puVar1;
  *puVar1 = CDXTexture__Helper_0059b960;
  puVar1[1] = CDXTexture__DecodeState_ResetCallbackContext;
  puVar1[2] = CDXTexture__Helper_0059b920;
  puVar1[3] = &LAB_0059ba70;
  puVar1[4] = 0;
  puVar1[5] = 0;
  puVar1[6] = 1;
  return;
}
