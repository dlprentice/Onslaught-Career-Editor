/* address: 0x00594fb6 */
/* name: CTexture__Helper_00594fb6 */
/* signature: void __stdcall CTexture__Helper_00594fb6(int param_1, int param_2, int param_3, int param_4) */


void CTexture__Helper_00594fb6(int param_1,int param_2,int param_3,int param_4)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) | 8;
    *(int *)(param_2 + 0x10) = param_3;
    *(undefined2 *)(param_2 + 0x14) = (undefined2)param_4;
  }
  return;
}
