/* address: 0x0058c3fe */
/* name: CTexture__Unk_0058c3fe */
/* signature: int __fastcall CTexture__Unk_0058c3fe(void * param_1) */


int __fastcall CTexture__Unk_0058c3fe(void *param_1)

{
  char *pcVar1;
  char *pcVar2;

  pcVar1 = *(char **)((int)param_1 + 4);
  if (*(char **)param_1 < pcVar1) {
    do {
      pcVar2 = *(char **)param_1;
      if (*pcVar2 == '\n') {
        return 1;
      }
      if (*pcVar2 == '\\') {
        if ((pcVar2 + 1 < pcVar1) && (pcVar2[1] == '\n')) {
          pcVar2 = pcVar2 + 2;
        }
        else {
          if ((pcVar1 <= pcVar2 + 2) || ((pcVar2[1] != '\r' || (pcVar2[2] != '\n'))))
          goto LAB_0058c445;
          pcVar2 = pcVar2 + 3;
        }
        *(int *)((int)param_1 + 0x1c) = *(int *)((int)param_1 + 0x1c) + 1;
      }
      else {
LAB_0058c445:
        pcVar2 = pcVar2 + 1;
      }
      *(char **)param_1 = pcVar2;
    } while (pcVar2 < *(char **)((int)param_1 + 4));
  }
  return 0;
}
