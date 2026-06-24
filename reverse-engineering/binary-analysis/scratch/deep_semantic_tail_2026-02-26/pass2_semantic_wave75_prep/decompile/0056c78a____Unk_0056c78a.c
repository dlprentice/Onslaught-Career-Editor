/* address: 0x0056c78a */
/* name: ___Unk_0056c78a */
/* signature: int __cdecl ___Unk_0056c78a(int param_1) */


int __cdecl ___Unk_0056c78a(int param_1)

{
  short *psVar1;

  psVar1 = &DAT_006566b4;
  do {
    if ((short)param_1 == *psVar1) {
      return 0;
    }
    psVar1 = psVar1 + 1;
  } while ((int)psVar1 < 0x6566c8);
  return 1;
}
