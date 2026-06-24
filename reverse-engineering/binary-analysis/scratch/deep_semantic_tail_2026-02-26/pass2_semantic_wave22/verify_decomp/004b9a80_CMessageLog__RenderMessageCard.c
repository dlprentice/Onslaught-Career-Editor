/* address: 0x004b9a80 */
/* name: CMessageLog__RenderMessageCard */
/* signature: int CMessageLog__RenderMessageCard(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMessageLog__RenderMessageCard(void)

{
  float fVar1;
  float p2;
  float p1;
  short *psVar2;
  int iVar3;
  int in_ECX;
  int iVar4;
  int iVar5;
  void *unaff_EDI;
  void *pvVar6;
  double dVar7;
  void *in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  int in_stack_00000014;
  int local_59c;
  int local_58c;
  char local_57c [20];
  short local_568 [690];

  pvVar6 = (void *)(*(int *)((int)DAT_008a9d84 + 0x1b8) + 9);
  local_58c = (int)(longlong)ROUND(in_stack_00000010 * _DAT_005d8c70);
  iVar3 = local_58c;
  if (0x55 < (int)pvVar6) {
    CConsole__Printf(&DAT_0066f580,s_FATAL_ERROR__mnessage_log_not_en_0063096c);
  }
  CMessage__WordWrapToLineBuffer(in_stack_00000004,(int)local_568,pvVar6,8,(int)unaff_EDI);
  iVar5 = 0;
  psVar2 = local_568;
  iVar4 = 8;
  do {
    if (*psVar2 != 0) {
      iVar5 = iVar5 + 1;
    }
    psVar2 = psVar2 + 0x56;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  fVar1 = (float)iVar5 * _DAT_005d8bc0 + _DAT_005d85cc;
  if (fVar1 < _DAT_005dbb74) {
    fVar1 = _DAT_005dbb74;
  }
  if (in_stack_00000014 == 0) {
    local_58c = (int)(longlong)ROUND(fVar1);
    CMessageLog__RenderPanelFrame();
    p1 = in_stack_00000008 + _DAT_005d85d8;
    fVar1 = (float)(iVar3 * 0x1000000 + 0xffffff);
    p2 = in_stack_0000000c + _DAT_005d85d8;
    RenderState_Set(0x13,1);
    RenderState_Set(0x14,2);
    RenderState_Set(0x17,8);
    RenderState_Set(0xf,1);
    RenderState_Set(0xe,1);
    RenderState_Set(7,1);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CVBufTexture__DrawSpriteEx
              (p1,p2,0.002,*(void **)(in_ECX + 0x14),0,0,1.0,0.0,fVar1,1.0,1.0,0.0,1.0,0.0,1.0);
    CExplosionInitThing__Helper_00482090();
    RenderState_Set(7,1);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    pvVar6 = DAT_008a9d84;
    iVar3 = CDropship__SelectPortraitIndex
                      (DAT_008a9d84,*(int *)((int)in_stack_00000004 + 0x18),unaff_EDI);
    pvVar6 = (void *)CMessageLog__Helper_004b82a0(pvVar6,iVar3,(int)unaff_EDI);
    CVBufTexture__DrawSpriteEx
              (p1 + _DAT_005d8c44,p2 + _DAT_005d8c44,0.003,pvVar6,0,0,1.0,0.0,fVar1,0.375,0.375,0.0,
               1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              (p1,p2,0.001,*(void **)(in_ECX + 0x10),0,0,1.0,0.0,fVar1,1.0,1.0,0.0,1.0,0.0,1.0);
    dVar7 = CDXEngine__Helper_0055dfe7
                      ((double)(*(float *)((int)in_stack_00000004 + 0x24) * _DAT_005dc770));
    local_59c = (int)(longlong)ROUND(dVar7);
    CDXEngine__Helper_0055dfe7
              ((double)((*(float *)((int)in_stack_00000004 + 0x24) -
                        (float)local_59c * _DAT_005dc76c) * _DAT_005dbc48));
    sprintf(local_57c,s__02d__02d__02d_0063095c);
    Text__AsciiToWideScratch(local_57c);
    CPlatform__Font(&DAT_0088a0a8,1);
    CDXEngine__Helper_004659a0();
    if (iVar5 < 4) {
      p2 = (p2 + _DAT_005db2bc) - (float)(iVar5 * 8 + -8);
    }
    if (iVar5 < 1) {
      return local_58c;
    }
    do {
      dVar7 = CDXEngine__Helper_0055dfe7((double)p2);
      p2 = (float)dVar7;
      CPlatform__Font(&DAT_0088a0a8,1);
      CDXEngine__Helper_004659a0();
      iVar5 = iVar5 + -1;
    } while (iVar5 != 0);
    return local_58c;
  }
  local_58c = (int)(longlong)ROUND(fVar1);
  return local_58c;
}
