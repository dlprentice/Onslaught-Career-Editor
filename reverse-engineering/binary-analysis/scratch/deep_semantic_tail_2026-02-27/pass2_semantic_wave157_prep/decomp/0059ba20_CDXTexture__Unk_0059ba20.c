/* address: 0x0059ba20 */
/* name: CDXTexture__Unk_0059ba20 */
/* signature: void __stdcall CDXTexture__Unk_0059ba20(void * param_1) */


void CDXTexture__Unk_0059ba20(void *param_1)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)((int)param_1 + 0x1b8);
  *puVar1 = CDXTexture__Helper_0059b960;
  puVar1[4] = 0;
  puVar1[5] = 0;
  puVar1[6] = 1;
  (**(code **)(*(int *)param_1 + 0x10))(param_1);
  (*(code *)**(undefined4 **)((int)param_1 + 0x1bc))(param_1);
  *(undefined4 *)((int)param_1 + 0xa4) = 0;
  return;
}
