/* address: 0x00403a50 */
/* name: CFrontEndPage__Unk_00403a50 */
/* signature: int __fastcall CFrontEndPage__Unk_00403a50(int param_1) */


int __fastcall CFrontEndPage__Unk_00403a50(int param_1)

{
  if ((((*(float *)(param_1 + 0x8c) != *(float *)(param_1 + 0x1c)) ||
       (*(float *)(param_1 + 0x90) != *(float *)(param_1 + 0x20))) ||
      (*(float *)(param_1 + 0x94) != *(float *)(param_1 + 0x24))) &&
     ((*(byte *)(param_1 + 0x2c) & 4) == 0)) {
    return 1;
  }
  return 0;
}
