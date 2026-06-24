/* address: 0x00581d49 */
/* name: CDXTexture__Unk_00581d49 */
/* signature: void __fastcall CDXTexture__Unk_00581d49(void * param_1) */


void __fastcall CDXTexture__Unk_00581d49(void *param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  int unaff_EDI;
  undefined1 local_28 [8];
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  int local_c;
  undefined4 local_8;

  local_10 = *(undefined4 *)((int)param_1 + 0x1060);
  local_14 = *(undefined4 *)((int)param_1 + 0x106c);
  local_18 = *(undefined4 *)((int)param_1 + 0x20);
  local_1c = *(undefined4 *)((int)param_1 + 0x34);
  local_20 = *(undefined4 *)((int)param_1 + 0x18);
  *(undefined4 *)((int)param_1 + 0x106c) = *(undefined4 *)((int)param_1 + 0x1070);
  *(undefined1 **)((int)param_1 + 0x20) = local_28;
  *(undefined4 *)((int)param_1 + 0x1060) = 1;
  *(undefined **)((int)param_1 + 0x34) = &DAT_00657980;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  if ((*(int *)((int)param_1 + 8) != 1) && (*(int *)((int)param_1 + 8) != 4)) {
    puVar1 = (undefined4 *)((int)param_1 + 0x1050);
    local_8 = *puVar1;
    piVar2 = (int *)((int)param_1 + 0x1054);
    local_c = *piVar2;
    *puVar1 = 1;
    *piVar2 = (int)param_1 + 0x24;
    CFastVB__Helper_00581279(param_1,(int)param_1 + 0x24,unaff_EDI);
    *puVar1 = local_8;
    *piVar2 = local_c;
  }
  (**(code **)(*(int *)param_1 + 8))(0,0,(int)param_1 + 0x24);
  (**(code **)(*(int *)param_1 + 4))(0,0,(int)param_1 + 0x24);
  *(undefined4 *)((int)param_1 + 0x1060) = local_10;
  *(undefined4 *)((int)param_1 + 0x106c) = local_14;
  *(undefined4 *)((int)param_1 + 0x20) = local_18;
  *(undefined4 *)((int)param_1 + 0x34) = local_1c;
  *(undefined4 *)((int)param_1 + 0x18) = local_20;
  return;
}
