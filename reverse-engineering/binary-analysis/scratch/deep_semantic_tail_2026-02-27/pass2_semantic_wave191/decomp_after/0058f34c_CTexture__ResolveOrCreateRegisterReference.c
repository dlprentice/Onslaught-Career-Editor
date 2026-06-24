/* address: 0x0058f34c */
/* name: CTexture__ResolveOrCreateRegisterReference */
/* signature: int CTexture__ResolveOrCreateRegisterReference(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__ResolveOrCreateRegisterReference(void)

{
  short sVar1;
  short *psVar2;
  int iVar3;
  void *in_ECX;
  void *this;
  void *unaff_EBX;
  void *in_stack_00000004;
  void *in_stack_00000008;
  void *in_stack_0000000c;
  short *in_stack_00000010;
  int in_stack_00000014;
  int *in_stack_00000018;
  undefined4 *in_stack_0000001c;
  int *in_stack_00000020;
  char *pcVar4;

  psVar2 = in_stack_00000010;
  do {
    sVar1 = *psVar2;
    psVar2 = (short *)((int)psVar2 + 1);
  } while ((char)sVar1 != '\0');
  if ((uint)((int)psVar2 - (int)((int)in_stack_00000010 + 1)) < 3) {
    CTexture__AppendDiagnosticMessage(in_stack_00000004,(int)in_stack_0000000c,0x7d5,0x5ecfc0);
    return -0x7fffbffb;
  }
  *in_stack_00000018 = 0;
  *in_stack_0000001c = 0;
  *in_stack_00000020 = 0;
  if (*in_stack_00000010 == DAT_005ecd94) {
    *in_stack_00000018 = 1;
    iVar3 = CTexture__FindIdentifierInHashTable
                      ((void *)((int)in_ECX + 0x1c),(int)in_stack_00000010,(int)unaff_EBX);
    if (iVar3 == 0) {
      iVar3 = CTexture__ParseVertexSemanticUsageToken
                        (this,in_stack_00000010 + 1,(void *)((int)&stack0x00000018 + 3),
                         (void *)((int)&stack0x00000010 + 3),unaff_EBX);
      if (iVar3 < 0) {
        pcVar4 = "Invalid input register \'%s\' specified";
        goto LAB_0058f3e0;
      }
      *in_stack_00000020 = *(int *)((int)in_ECX + 0x58);
      CTexture__InsertSymbolNodeInHashTable
                ((void *)((int)in_ECX + 0x1c),(int)in_stack_00000010,*(void **)((int)in_ECX + 0x58),
                 1,(int)unaff_EBX);
      *(int *)((int)in_ECX + 0x58) = *(int *)((int)in_ECX + 0x58) + 1;
    }
    else {
      *in_stack_00000020 = *(int *)(iVar3 + 4);
    }
    if (in_stack_00000014 == 0) {
      return 0;
    }
    pcVar4 = "addressing operations are not allowed on input registers \'%s\'";
  }
  else if (*in_stack_00000010 == DAT_005ecd90) {
    *in_stack_00000018 = 0;
    iVar3 = CTexture__FindIdentifierInHashTable
                      ((void *)((int)in_ECX + 0x38),(int)in_stack_00000010,(int)unaff_EBX);
    if (iVar3 == 0) {
      *in_stack_00000020 = *(int *)((int)in_ECX + 0x5c);
      CTexture__InsertSymbolNodeInHashTable
                ((void *)((int)in_ECX + 0x38),(int)in_stack_00000010,*(void **)((int)in_ECX + 0x5c),
                 1,(int)unaff_EBX);
      *(int *)((int)in_ECX + 0x5c) = *(int *)((int)in_ECX + 0x5c) + 1;
    }
    else {
      *in_stack_00000020 = *(int *)(iVar3 + 4);
    }
    if (in_stack_00000014 == 0) {
      return 0;
    }
    pcVar4 = "addressing operations not allowed on temporary registers \'%s\'";
  }
  else {
    sVar1 = *in_stack_00000010;
    if (((sVar1 == DAT_005ecf14) || (sVar1 == DAT_005ecf10)) || (sVar1 == DAT_005ecf0c)) {
      if (*in_stack_00000010 == DAT_005ecf10) {
        *in_stack_00000018 = 0xe;
      }
      else {
        *in_stack_00000018 = (-(uint)(*in_stack_00000010 != DAT_005ecf0c) & 0xfffffffb) + 7;
      }
      iVar3 = CTexture__FindIdentifierInHashTable(in_ECX,(int)in_stack_00000010,(int)unaff_EBX);
      if (iVar3 == 0) {
        iVar3 = CTexture__Helper_0059930d
                          (in_stack_00000008,in_stack_0000000c,in_stack_00000010,&stack0x0000001c,
                           unaff_EBX);
        if (iVar3 < 0) {
          return iVar3;
        }
        if (in_stack_0000001c == (undefined4 *)0x0) {
          CTexture__AppendDiagnosticMessage(in_stack_00000004,(int)in_stack_0000000c,0x7d5,0x5ece58)
          ;
          return -0x7fffbffb;
        }
        *in_stack_00000020 = *(int *)((int)in_ECX + 0x54);
        CTexture__InsertSymbolNodeInHashTable
                  (in_ECX,(int)in_stack_00000010,*(void **)((int)in_ECX + 0x54),
                   (int)in_stack_0000001c,(int)unaff_EBX);
        *(int *)((int)in_ECX + 0x54) = *(int *)((int)in_ECX + 0x54) + (int)in_stack_0000001c;
        *(int *)((int)in_ECX + 0x60) = *(int *)((int)in_ECX + 0x60) + 1;
      }
      else {
        *in_stack_00000020 = *(int *)(iVar3 + 4);
        in_stack_0000001c = *(undefined4 **)(iVar3 + 8);
      }
      if (in_stack_00000014 == 0) {
        return 0;
      }
      if (in_stack_0000001c < *(undefined4 **)(in_stack_00000014 + 0x18)) {
        CTexture__AppendDiagnosticMessage(in_stack_00000004,(int)in_stack_0000000c,0x7d5,0x5ece08);
        return -0x7fffbffb;
      }
      *in_stack_00000020 = *in_stack_00000020 + (int)*(undefined4 **)(in_stack_00000014 + 0x18);
      return 0;
    }
    pcVar4 =
    "\'%s\' is not a valid register name.  Registers must start with v_, r_, c_, b_, or i_ depending on the register type."
    ;
  }
LAB_0058f3e0:
  CTexture__AppendDiagnosticMessage(in_stack_00000004,(int)in_stack_0000000c,0x7d5,(int)pcVar4);
  return -0x7fffbffb;
}
