/* address: 0x0058c95c */
/* name: CTexture__AppendDiagnosticMessageDedup */
/* signature: int __cdecl CTexture__AppendDiagnosticMessageDedup(void * param_1, int param_2, int param_3) */


int __cdecl CTexture__AppendDiagnosticMessageDedup(void *param_1,int param_2,int param_3)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  void *pvVar6;
  int unaff_EBX;
  void *pvVar7;
  undefined1 *puVar8;
  void *in_stack_00000010;
  undefined1 local_1010 [4072];
  undefined4 uStackY_28;
  void *pvVar9;

  CRT__AllocaProbe();
  puVar8 = local_1010;
  pvVar9 = (void *)0xffe;
  iVar3 = CDXTexture__InsertOrFindKeyInSortedTable
                    (param_1,param_3,(uint)&stack0xfffffff8,(void *)0xffe);
  if (-1 < iVar3) {
    puVar1 = (uint *)(*(int *)((int)param_1 + 0x1c) + unaff_EBX * 4);
    uVar2 = *puVar1;
    uVar4 = uVar2 & 0xf;
    if (uVar4 == 0xf) {
      piVar5 = (int *)((int)param_1 + 8);
      pvVar7 = (void *)0xffe;
    }
    else {
      piVar5 = (int *)((int)param_1 + 0xc);
      if ((((*(uint *)((int)param_1 + 0x10) == 0) || (uVar4 == 0)) ||
          (*(uint *)((int)param_1 + 0x10) < uVar4)) ||
         (((uVar2 & 0x10) != 0 && ((uVar2 & 0x20) != 0)))) {
        return 0;
      }
      *puVar1 = uVar2 | 0x20;
      pvVar7 = pvVar9;
    }
    if (param_2 != 0) {
      if (*(int *)(param_2 + 0x10) != 0) {
        iVar3 = CTexture__Helper_005d075f(local_1010,0xffe,&DAT_005ea38c);
        if (iVar3 < 0) {
          iVar3 = 0xffe;
        }
        puVar8 = local_1010 + iVar3;
        pvVar7 = (void *)(0xffe - iVar3);
      }
      pvVar6 = (void *)CTexture__Helper_005d075f(puVar8,(int)pvVar7,"(%u): ");
      if ((int)pvVar6 < 0) {
        pvVar6 = pvVar7;
      }
      puVar8 = puVar8 + (int)pvVar6;
      pvVar7 = (void *)((int)pvVar7 - (int)pvVar6);
    }
    if (param_3 != 0) {
      uStackY_28 = 0x58ca73;
      pvVar6 = (void *)CTexture__Helper_005d075f(puVar8,(int)pvVar7,"%s X%u: ");
      if ((int)pvVar6 < 0) {
        pvVar6 = pvVar7;
      }
      puVar8 = puVar8 + (int)pvVar6;
      pvVar7 = (void *)((int)pvVar7 - (int)pvVar6);
    }
    pvVar6 = (void *)CRT__VsnprintfAndTerminate_005d070f
                               (puVar8,(int)pvVar7,in_stack_00000010,&stack0x00000014);
    if ((int)pvVar6 < 0) {
      pvVar6 = pvVar7;
    }
    (puVar8 + (int)pvVar6)[1] = 0;
    puVar8[(int)pvVar6] = 10;
    *piVar5 = *piVar5 + 1;
    iVar3 = CTexture__AppendDiagnosticTextLine(param_1,local_1010,pvVar9);
  }
  return iVar3;
}
