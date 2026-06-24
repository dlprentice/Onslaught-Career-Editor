/* address: 0x00589e73 */
/* name: CTexture__Unk_00589e73 */
/* signature: int __fastcall CTexture__Unk_00589e73(int param_1) */


int __fastcall CTexture__Unk_00589e73(int param_1)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  char local_108 [256];
  uint local_8;

  pcVar5 = (char *)**(undefined4 **)(param_1 + 0x54);
  CTexture__Unk_0058c3fe(*(undefined4 **)(param_1 + 0x54));
  if (*(int *)(param_1 + 0x38) != 0) {
    for (; (pcVar5 < (char *)**(uint **)(param_1 + 0x54) && ((*pcVar5 == ' ' || (*pcVar5 == '\t'))))
        ; pcVar5 = pcVar5 + 1) {
    }
    local_8 = 0;
    pcVar4 = pcVar5 + 2;
    pcVar3 = pcVar5 + 1;
    do {
      pcVar2 = (char *)**(undefined4 **)(param_1 + 0x54);
      if (pcVar2 <= pcVar5) break;
      cVar1 = *pcVar5;
      if (cVar1 == '\\') {
        if ((pcVar3 < pcVar2) && (*pcVar3 == '\n')) {
          pcVar5 = pcVar5 + 2;
          pcVar3 = pcVar3 + 2;
          pcVar4 = pcVar4 + 2;
        }
        else {
          if ((pcVar2 <= pcVar4) || ((*pcVar3 != '\r' || (*pcVar4 != '\n')))) goto LAB_00589ef2;
          pcVar5 = pcVar5 + 3;
          pcVar3 = pcVar3 + 3;
          pcVar4 = pcVar4 + 3;
        }
      }
      else {
LAB_00589ef2:
        if (cVar1 != '\r') {
          local_108[local_8] = cVar1;
          local_8 = local_8 + 1;
        }
        pcVar5 = pcVar5 + 1;
        pcVar3 = pcVar3 + 1;
        pcVar4 = pcVar4 + 1;
      }
    } while (local_8 < 0xff);
    local_108[local_8] = '\0';
    CTexture__Helper_0058c893((void *)(param_1 + 4),param_1 + 0x60,0,0x5ea430);
    *(undefined4 *)(param_1 + 0x30) = 1;
    *(undefined4 *)(param_1 + 0x2c) = 1;
  }
  return 0;
}
