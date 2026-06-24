/* address: 0x0057ca6a */
/* name: CDXTexture__Unk_0057ca6a */
/* signature: int CDXTexture__Unk_0057ca6a(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_0057ca6a(void)

{
  int *piVar1;
  int *in_ECX;
  int iVar2;
  int *piVar3;
  void *unaff_EDI;
  int *piVar4;
  void *in_stack_00000004;
  void *in_stack_00000008;
  int *in_stack_0000000c;
  int in_stack_00000010;
  int local_24 [8];

  piVar1 = in_stack_0000000c;
  if ((in_stack_00000004 == (void *)0x0) || (in_stack_00000008 == (void *)0x0)) {
    iVar2 = -0x7789f794;
  }
  else {
    if ((in_stack_0000000c != (int *)0x0) || (in_stack_00000010 != 0)) {
      local_24[0] = 0;
      local_24[1] = 5;
      local_24[2] = 4;
      local_24[3] = 1;
      local_24[4] = 3;
      local_24[5] = 2;
      local_24[6] = 6;
      local_24[7] = 0;
      do {
        in_ECX[0x10] = in_stack_00000010;
        iVar2 = local_24[local_24[7]];
        in_ECX[0x12] = iVar2;
        in_ECX[0x11] = 3;
        if (iVar2 == 0) {
          in_stack_0000000c =
               (int *)CDXTexture__DecodeBmpFromMemory
                                (in_ECX,in_stack_00000004,in_stack_00000008,(uint)unaff_EDI);
        }
        else if (iVar2 == 1) {
          in_stack_0000000c =
               (int *)CDXTexture__Unk_0057af0a((int)in_stack_00000004,(int)in_stack_00000008);
        }
        else if (iVar2 == 2) {
          in_stack_0000000c =
               (int *)CDXTexture__Unk_0057b182
                                (in_ECX,in_stack_00000004,in_stack_00000008,(uint)unaff_EDI);
        }
        else if (iVar2 == 3) {
          in_stack_0000000c =
               (int *)CDXTexture__Unk_0057b9ce((int)in_stack_00000004,(int)in_stack_00000008);
        }
        else if (iVar2 == 4) {
          in_stack_0000000c =
               (int *)CDXTexture__Helper_0057bf1f
                                (in_ECX,in_stack_00000004,in_stack_00000008,unaff_EDI);
        }
        else if (iVar2 == 5) {
          in_stack_0000000c =
               (int *)CDXTexture__Unk_0057b6fa
                                (in_ECX,in_stack_00000004,in_stack_00000008,(uint)unaff_EDI);
        }
        else if (iVar2 == 6) {
          in_stack_0000000c =
               (int *)CDXTexture__Unk_00579e08(in_ECX,in_stack_00000004,in_stack_00000008,unaff_EDI)
          ;
        }
        if (-1 < (int)in_stack_0000000c) break;
        if (((void *)in_ECX[1] != (void *)0x0) && (in_ECX[0xe] != 0)) {
          OID__FreeObject_Callback((void *)in_ECX[1]);
        }
        if (((void *)in_ECX[2] != (void *)0x0) && (in_ECX[0xf] != 0)) {
          OID__FreeObject_Callback((void *)in_ECX[2]);
        }
        if ((void *)in_ECX[0x13] != (void *)0x0) {
          CDXTexture__Helper_00579d17((void *)in_ECX[0x13],(void *)0x1,(int)unaff_EDI);
        }
        if ((void *)in_ECX[0x14] != (void *)0x0) {
          CDXTexture__Helper_00579d17((void *)in_ECX[0x14],(void *)0x1,(int)unaff_EDI);
        }
        local_24[7] = local_24[7] + 1;
        in_ECX[1] = 0;
        in_ECX[2] = 0;
        in_ECX[0xe] = 0;
        in_ECX[0xf] = 0;
        in_ECX[0x13] = 0;
        in_ECX[0x14] = 0;
      } while ((uint)local_24[7] < 7);
      iVar2 = 7;
      if (local_24[7] == 7) {
        return -0x7789f4a7;
      }
      piVar4 = piVar1;
      piVar3 = in_ECX;
      if (piVar1 != (int *)0x0) {
        for (; iVar2 != 0; iVar2 = iVar2 + -1) {
          *piVar4 = 0;
          piVar4 = piVar4 + 1;
        }
        *piVar1 = in_ECX[3];
        piVar1[1] = in_ECX[4];
        piVar1[2] = in_ECX[5];
        piVar1[3] = 1;
        iVar2 = CDXTexture__Helper_00574476(*in_ECX);
        piVar1[4] = iVar2;
        piVar1[5] = in_ECX[0x11];
        piVar1[6] = in_ECX[0x12];
        for (piVar4 = in_ECX; piVar4[0x13] != 0; piVar4 = (int *)piVar4[0x13]) {
          piVar1[3] = piVar1[3] + 1;
        }
      }
      do {
        for (; in_ECX != (int *)0x0; in_ECX = (int *)in_ECX[0x13]) {
          in_ECX[8] = in_ECX[3];
          in_ECX[9] = in_ECX[4];
          in_ECX[6] = 0;
          in_ECX[7] = 0;
          in_ECX[10] = 0;
          in_ECX[0xb] = in_ECX[5];
        }
        in_ECX = (int *)piVar3[0x14];
        piVar3 = in_ECX;
      } while (in_ECX != (int *)0x0);
    }
    iVar2 = 0;
  }
  return iVar2;
}
