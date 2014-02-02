surface hair (float Ka = 1, Kd = .6, Ks = .35, roughness = .15;
	      color rootcolor = color (.109, .037, .007);
	      color tipcolor = color (.519, .325, .125);
	      color specularcolor = (color(1) + tipcolor) / 2;
	     )
{
    vector T = normalize (dPdv); /* tangent along length of hair */
    vector V = -normalize(I);    /* V is the view vector */
    color Cspec = 0, Cdiff = 0;  /* collect specular & diffuse light */
    float cosang;

    /* Loop over lights, catch highlights as if this was a thin cylinder */
    illuminance (P) {
	cosang = abs(cos (abs (acos (T.normalize(L)) - acos (-T.V))));
	Cspec += Cl * v * pow (cosang, 1/roughness);
	Cdiff += Cl * v;
	/* We multipled by v to make it darker at the roots.  This
	 * assumes v=0 at the root, v=1 at the tip.
	 */
    }

    Oi = Os;
    Ci = Oi * (mix(rootcolor, tipcolor, v) * (Ka*ambient() + Kd*Cdiff)
                 + (Ks * Cspec * specularcolor));
}






















