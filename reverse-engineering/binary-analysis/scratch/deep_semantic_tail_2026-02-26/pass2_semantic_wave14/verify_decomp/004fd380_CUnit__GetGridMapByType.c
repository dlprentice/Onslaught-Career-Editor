/* address: 0x004fd380 */
/* name: CUnit__GetGridMapByType */
/* signature: int __fastcall CUnit__GetGridMapByType(int param_1) */


int __fastcall CUnit__GetGridMapByType(int param_1)

{
  if (*(int *)(param_1 + 0x164) != 0) {
    switch(*(undefined4 *)(*(int *)(param_1 + 0x164) + 0xfc)) {
    case 1:
      return DAT_00855290;
    case 2:
      return DAT_00855294;
    case 3:
    case 4:
      return DAT_00855298;
    }
  }
  return 0;
}
