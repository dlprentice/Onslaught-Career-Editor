/* address: 0x0050a9c0 */
/* name: CSPtrSetArray19__InitAndResetState */
/* signature: void * __fastcall CSPtrSetArray19__InitAndResetState(void * param_1) */


void * __fastcall CSPtrSetArray19__InitAndResetState(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d5b61;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CSPtrSet__Init(param_1);
  local_4 = 0;
  CSPtrSet__Init((void *)((int)param_1 + 0x10));
  local_4._0_1_ = 1;
  CSPtrSet__Init((void *)((int)param_1 + 0x20));
  local_4._0_1_ = 2;
  CSPtrSet__Init((void *)((int)param_1 + 0x30));
  local_4._0_1_ = 3;
  CSPtrSet__Init((void *)((int)param_1 + 0x40));
  local_4._0_1_ = 4;
  CSPtrSet__Init((void *)((int)param_1 + 0x50));
  local_4._0_1_ = 5;
  CSPtrSet__Init((void *)((int)param_1 + 0x60));
  local_4._0_1_ = 6;
  CSPtrSet__Init((void *)((int)param_1 + 0x70));
  local_4._0_1_ = 7;
  CSPtrSet__Init((void *)((int)param_1 + 0x80));
  local_4._0_1_ = 8;
  CSPtrSet__Init((void *)((int)param_1 + 0x90));
  local_4._0_1_ = 9;
  CSPtrSet__Init((void *)((int)param_1 + 0xa0));
  local_4._0_1_ = 10;
  CSPtrSet__Init((void *)((int)param_1 + 0xb0));
  local_4._0_1_ = 0xb;
  CSPtrSet__Init((void *)((int)param_1 + 0xc0));
  local_4._0_1_ = 0xc;
  CSPtrSet__Init((void *)((int)param_1 + 0xd0));
  local_4._0_1_ = 0xd;
  CSPtrSet__Init((void *)((int)param_1 + 0xe0));
  local_4._0_1_ = 0xe;
  CSPtrSet__Init((void *)((int)param_1 + 0xf0));
  local_4._0_1_ = 0xf;
  CSPtrSet__Init((void *)((int)param_1 + 0x100));
  local_4._0_1_ = 0x10;
  CSPtrSet__Init((void *)((int)param_1 + 0x110));
  local_4 = CONCAT31(local_4._1_3_,0x11);
  CSPtrSet__Init((void *)((int)param_1 + 0x120));
  *(undefined4 *)((int)param_1 + 0x200) = 0;
  *(undefined4 *)((int)param_1 + 0x204) = 0;
  *(undefined4 *)((int)param_1 + 0x208) = 0;
  iVar2 = 0x1a;
  *(undefined4 *)((int)param_1 + 0x26c) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x270) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x274) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x278) = 0xffffffff;
  puVar1 = (undefined4 *)((int)param_1 + 0x198);
  do {
    puVar1[-0x1a] = 0;
    *puVar1 = 0;
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  *(undefined4 *)((int)param_1 + 0x20c) = 0;
  *(undefined4 *)((int)param_1 + 0x210) = 0;
  *(undefined4 *)((int)param_1 + 0x214) = 0;
  *(undefined4 *)((int)param_1 + 0x218) = 0;
  ExceptionList = local_c;
  return param_1;
}
