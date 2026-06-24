/* address: 0x0055f2a7 */
/* name: CDropship__FindSubstringW */
/* signature: short * __cdecl CDropship__FindSubstringW(void * param_1, void * param_2) */


short * __cdecl CDropship__FindSubstringW(void *param_1,void *param_2)

{
  short *psVar1;

  do {
    if (*(short *)param_1 == 0) {
      return (short *)0x0;
    }
    psVar1 = param_2;
    do {
      if ((*psVar1 == 0) || (*(short *)(((int)param_1 - (int)param_2) + (int)psVar1) != *psVar1))
      break;
      psVar1 = psVar1 + 1;
    } while (*(short *)(((int)param_1 - (int)param_2) + (int)psVar1) != 0);
    if (*psVar1 == 0) {
      return param_1;
    }
    param_1 = (void *)((int)param_1 + 2);
  } while( true );
}
