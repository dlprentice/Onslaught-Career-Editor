/* address: 0x00595030 */
/* name: CTexture__Unk_00595030 */
/* signature: void __stdcall CTexture__Unk_00595030(int param_1, int param_2, int param_3, int param_4, void * param_5) */


void CTexture__Unk_00595030(int param_1,int param_2,int param_3,int param_4,void *param_5)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    if (param_3 != 0) {
      *(int *)(param_2 + 0x30) = param_3;
    }
    if (param_5 != (void *)0x0) {
      *(undefined4 *)(param_2 + 0x34) = *(undefined4 *)param_5;
      *(undefined4 *)(param_2 + 0x38) = *(undefined4 *)((int)param_5 + 4);
      *(undefined2 *)(param_2 + 0x3c) = *(undefined2 *)((int)param_5 + 8);
      if (param_4 == 0) {
        param_4 = 1;
      }
    }
    *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) | 0x10;
    *(undefined2 *)(param_2 + 0x16) = (undefined2)param_4;
  }
  return;
}
