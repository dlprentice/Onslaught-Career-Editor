/* address: 0x00596341 */
/* name: CFastVB__Helper_00596341 */
/* signature: void __stdcall CFastVB__Helper_00596341(void * param_1) */


void CFastVB__Helper_00596341(void *param_1)

{
  *(undefined1 **)param_1 = &LAB_00595ea0;
  *(undefined1 **)((int)param_1 + 4) = &LAB_00595f3e;
  *(undefined1 **)((int)param_1 + 8) = &LAB_00596028;
  *(code **)((int)param_1 + 0xc) = CDXTexture__MultiplyMatrix4x4_InPlaceSafe;
  *(code **)((int)param_1 + 0x10) = CDXTexture__MultiplyMatrix4x4_Safe;
  *(undefined1 **)((int)param_1 + 0x14) = &LAB_00595f09;
  *(undefined1 **)((int)param_1 + 0x18) = &LAB_00595fc9;
  *(code **)((int)param_1 + 0x1c) = CDXTexture__NormalizeVec3Fast;
  *(undefined1 **)((int)param_1 + 0x88) = &LAB_00596028;
  return;
}
